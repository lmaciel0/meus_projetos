import re
import threading
from dataclasses import dataclass, field

import language_tool_python

# Categorias do LanguageTool que são sugestões de estilo/registro, não erros.
# Para texto de ficção elas não são aplicadas: viram apenas observações.
CATEGORIAS_ESTILO = {"STYLE", "FORMAL", "REDUNDANCY", "REPETITIONS_STYLE", "COLLOQUIALISMS", "SEMANTICS"}
TIPOS_ESTILO = {"style", "register", "locale-violation"}

# Regras de concordância erram com mais frequência em frases longas, então não são
# aplicadas sozinhas: o autor decide cada uma. A maioria está em GRAMMAR (exceto crase,
# que é confiável); algumas o LanguageTool classifica em outras categorias.
CATEGORIAS_SUGESTAO = {"GRAMMAR"}
REGRAS_SUGESTAO = {"HAVIAM_MUITAS_BR", "CONFUSÃO_MEIA_MEIO_ADJETIVO"}

MOTIVO_FIXA = "Correção fixa do seu dicionário"


class ErroCorrecao(Exception):
    """Erro com mensagem amigável para exibir na interface."""


@dataclass
class Resultado:
    texto_corrigido: str
    # Cada correção: offset, tamanho, original, corrigido, motivo,
    # tipo ("automatica" ou "sugestao") e aceita (bool).
    correcoes: list[dict] = field(default_factory=list)
    observacoes: str = ""


_tool: language_tool_python.LanguageTool | None = None
# O Streamlit roda cada sessão numa thread: sem a trava, dois cliques simultâneos
# na primeira correção iniciariam dois servidores Java.
_tool_lock = threading.Lock()


def _get_tool() -> language_tool_python.LanguageTool:
    global _tool
    with _tool_lock:
        if _tool is None:
            try:
                _tool = language_tool_python.LanguageTool("pt-BR")
            except Exception as e:
                raise ErroCorrecao(f"Não foi possível iniciar o LanguageTool (é preciso ter Java instalado): {e}") from e
        return _tool


def _e_atribuicao_de_dialogo(texto: str, match) -> bool:
    """'— Vem? perguntou ele' — em diálogo, o verbo após ?/! fica minúsculo."""
    if match.rule_id != "UPPERCASE_SENTENCE_START":
        return False
    antes = texto[: match.offset].rstrip()
    inicio_linha = texto.rfind("\n", 0, match.offset) + 1
    return antes.endswith(("?", "!")) and any(t in texto[inicio_linha : match.offset] for t in ("—", "–"))


def _escolher(trecho: str, replacements: list[str]) -> str:
    """Primeira sugestão, salvo quando ela reescreve palavras que estavam certas.

    Em "uma ves" o corretor ortográfico sugere primeiro "um aves" (move o espaço) e só
    depois "uma vez". Se a primeira sugestão mantém o número de palavras, fica a que
    altera menos palavras; empates mantêm a ordem do LanguageTool. Junções como
    "com migo" → "comigo" mudam o número de palavras e não são afetadas.
    """
    palavras, primeira = trecho.split(), replacements[0]
    if len(palavras) < 2 or len(primeira.split()) != len(palavras):
        return primeira
    candidatas = [r for r in replacements if len(r.split()) == len(palavras)]
    return min(candidatas, key=lambda r: sum(a != b for a, b in zip(palavras, r.split())))


def _sugestao(trecho: str, match) -> str | None:
    """Melhor sugestão, sem capitalizar uma palavra que o autor escreveu em minúscula.

    Retorna None quando, depois disso, não sobra nada a corrigir (ex.: "brasil" → "Brasil").
    """
    if not match.replacements:
        return None
    sugestao = _escolher(trecho, match.replacements)
    # Siglas ("eua" → "EUA") não são rebaixadas: viraria "eUA".
    if match.category != "CASING" and trecho[:1].islower() and sugestao[:1].isupper() and not sugestao[1:2].isupper():
        sugestao = sugestao[0].lower() + sugestao[1:]
    return sugestao if sugestao != trecho else None


def _e_estilo(match) -> bool:
    return match.category in CATEGORIAS_ESTILO or match.rule_issue_type in TIPOS_ESTILO


def _e_sugestao(match) -> bool:
    if match.rule_id in REGRAS_SUGESTAO:
        return True
    return match.category in CATEGORIAS_SUGESTAO and "CRASE" not in match.rule_id


def aplicar(texto: str, correcoes: list[dict]) -> str:
    """Aplica ao texto original as correções marcadas como aceitas."""
    for c in sorted(correcoes, key=lambda c: c["offset"], reverse=True):
        if c["aceita"]:
            texto = texto[: c["offset"]] + c["corrigido"] + texto[c["offset"] + c["tamanho"] :]
    return texto


def _correcoes_fixas(texto: str, fixas: dict[str, str]) -> list[dict]:
    """Correções do dicionário pessoal ("tava" → "estava"), só em palavras inteiras."""
    encontradas = []
    for original, corrigido in fixas.items():
        for achado in re.finditer(rf"(?<!\w){re.escape(original)}(?!\w)", texto, re.IGNORECASE):
            trecho = achado.group()
            # "Tava" no início da frase vira "Estava".
            substituto = corrigido[:1].upper() + corrigido[1:] if trecho[:1].isupper() else corrigido
            if substituto != trecho:
                encontradas.append(
                    {
                        "offset": achado.start(),
                        "tamanho": len(trecho),
                        "original": trecho,
                        "corrigido": substituto,
                        "motivo": MOTIVO_FIXA,
                        "tipo": "automatica",
                        "aceita": True,
                    }
                )
    # Entradas que se sobrepõem ("tava" e "tava bem"): fica a primeira no texto.
    resultado, fim_anterior = [], 0
    for c in sorted(encontradas, key=lambda c: (c["offset"], -c["tamanho"])):
        if c["offset"] >= fim_anterior:
            resultado.append(c)
            fim_anterior = c["offset"] + c["tamanho"]
    return resultado


def corrigir(texto: str, ignoradas: set[str] = frozenset(), fixas: dict[str, str] | None = None) -> Resultado:
    """Revisa o texto. `ignoradas` e as chaves de `fixas` vêm do dicionário pessoal, em minúsculas."""
    try:
        matches = _get_tool().check(texto)
    except ErroCorrecao:
        raise
    except Exception as e:
        raise ErroCorrecao(f"Erro ao verificar o texto: {e}") from e

    correcoes = _correcoes_fixas(texto, fixas or {})
    faixas_fixas = [(c["offset"], c["offset"] + c["tamanho"]) for c in correcoes]
    observacoes, fim_anterior = [], 0
    for m in sorted(matches, key=lambda m: m.offset):
        trecho = texto[m.offset : m.offset + m.error_length]
        if _e_atribuicao_de_dialogo(texto, m) or trecho.lower() in ignoradas:
            continue
        # O dicionário pessoal tem prioridade sobre o que o LanguageTool marcou no mesmo trecho.
        if any(m.offset < fim and inicio < m.offset + m.error_length for inicio, fim in faixas_fixas):
            continue
        corrigido = _sugestao(trecho, m)
        # Correções sobrepostas não podem ser aplicadas juntas; fica a primeira e
        # as demais viram observação em vez de sumirem.
        if _e_estilo(m) or corrigido is None or m.offset < fim_anterior:
            sugestao = f" (sugestão: “{m.replacements[0]}”)" if m.replacements else ""
            observacoes.append(f"“{trecho}”: {m.message}{sugestao}")
            continue
        fim_anterior = m.offset + m.error_length

        motivo = m.message
        alternativas = [r for r in m.replacements if r.lower() != corrigido.lower()][:2]
        if alternativas:
            motivo += f" (alternativas: {', '.join(alternativas)})"
        automatica = not _e_sugestao(m)
        correcoes.append(
            {
                "offset": m.offset,
                "tamanho": m.error_length,
                "original": trecho,
                "corrigido": corrigido,
                "motivo": motivo,
                "tipo": "automatica" if automatica else "sugestao",
                "aceita": automatica,
            }
        )

    correcoes.sort(key=lambda c: c["offset"])
    return Resultado(
        texto_corrigido=aplicar(texto, correcoes),
        correcoes=correcoes,
        observacoes="\n".join(f"- {o}" for o in observacoes),
    )
