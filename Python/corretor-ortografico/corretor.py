import bisect
import re
import threading
import unicodedata
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

# Sugestões com mais letras diferentes que isso (sem contar acentos) quase sempre estão
# erradas ("noslençois" → "moquencos", "Rhyssa" → "Chica"): viram checkbox, não são aplicadas.
DISTANCIA_MAXIMA_AUTOMATICA = 2

# Palavras curtas que costumam grudar na seguinte ao digitar ("decasa", "comfome", "foiuma").
# Sem as de uma letra ("a", "o", "é"): o LanguageTool sugere separações absurdas com elas ("a pra").
PALAVRAS_DE_LIGACAO = {
    "as", "os", "um", "uma", "uns", "umas", "de", "da", "do", "das", "dos", "em", "na", "no",
    "nas", "nos", "num", "numa", "ao", "aos", "com", "sem", "por", "pra", "pro", "para", "que", "se",
    "me", "te", "lhe", "eu", "ele", "ela", "meu", "minha", "seu", "sua", "foi", "era", "já", "não",
}


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


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if not unicodedata.combining(c))


def _distancia(a: str, b: str) -> int:
    """Letras inseridas, removidas, trocadas ou invertidas ("ev" → "ve" conta 1), ignorando acentos."""
    a, b = _sem_acento(a), _sem_acento(b)
    anterior2, anterior = None, list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        atual = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            atual[j] = min(anterior[j] + 1, atual[j - 1] + 1, anterior[j - 1] + (a[i - 1] != b[j - 1]))
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                atual[j] = min(atual[j], anterior2[j - 2] + 1)
        anterior2, anterior = anterior, atual
    return anterior[-1]


def _pode_estar_grudada(trecho: str, match) -> bool:
    """Palavra que o corretor ortográfico não soube corrigir bem: talvez sejam duas sem espaço."""
    if not match.rule_id.startswith("MORFOLOGIK") or len(trecho) < 4 or not trecho.isalpha():
        return False
    if not match.replacements:
        return True
    return _distancia(trecho, _escolher(trecho, match.replacements)) > DISTANCIA_MAXIMA_AUTOMATICA


def _separar_grudadas(trechos: set[str]) -> dict[str, str]:
    """Tenta "noslençois" → "nos lençóis": separa em cada posição e pergunta ao LanguageTool.

    As duas partes precisam ser palavras válidas; na segunda só se aceita corrigir acento.
    Aceitar mais que isso inventa frases ("momentum" → "mome num"). Todas as tentativas
    vão numa única verificação, uma por linha.
    """
    tentativas = [(t, t[:i], t[i:]) for t in sorted(trechos) for i in range(1, len(t))]
    inicios, posicao = [], 0
    for _, esquerda, direita in tentativas:
        inicios.append(posicao)
        posicao += len(esquerda) + len(direita) + 2  # espaço entre as partes e "\n"
    texto = "\n".join(f"{esquerda} {direita}" for _, esquerda, direita in tentativas)

    erros = [[] for _ in tentativas]
    for m in _get_tool().check(texto):
        if m.rule_id.startswith("MORFOLOGIK"):
            erros[bisect.bisect_right(inicios, m.offset) - 1].append(m)

    separadas: dict[str, str] = {}
    for (trecho, esquerda, direita), inicio, ms in zip(tentativas, inicios, erros):
        if trecho in separadas:
            continue
        if not ms:
            segunda = direita
        elif len(ms) == 1 and ms[0].offset == inicio + len(esquerda) + 1 and ms[0].error_length == len(direita):
            segunda = _sugestao(direita, ms[0])
            if segunda is None or " " in segunda or _distancia(direita, segunda) > 0:
                continue
        else:
            continue
        separadas[trecho] = f"{esquerda} {segunda}"
    return separadas


def _versao_com_espaco(trecho: str, replacements: list[str]) -> str | None:
    """A sugestão que só insere um espaço ("decasa" → "de casa"), se for plausível.

    O LanguageTool acrescenta separações absurdas a muitas palavras ("tempera tira",
    "quero d", "la bios"). As que valem a dúvida começam com uma palavra de ligação.
    """
    if " " in trecho:
        return None
    for r in replacements:
        primeira, _, segunda = r.partition(" ")
        if r.replace(" ", "").lower() == trecho.lower() and primeira.lower() in PALAVRAS_DE_LIGACAO and len(segunda) > 1:
            return r
    return None


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
        grudadas = {
            trecho
            for m in matches
            if _pode_estar_grudada(trecho := texto[m.offset : m.offset + m.error_length], m)
            and trecho.lower() not in ignoradas
        }
        separadas = _separar_grudadas(grudadas) if grudadas else {}
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
        separada = separadas.get(trecho)
        corrigido = separada or _sugestao(trecho, m)
        # Correções sobrepostas não podem ser aplicadas juntas; fica a primeira e
        # as demais viram observação em vez de sumirem.
        if _e_estilo(m) or corrigido is None or m.offset < fim_anterior:
            sugestao = f" (sugestão: “{m.replacements[0]}”)" if m.replacements else ""
            observacoes.append(f"“{trecho}”: {m.message}{sugestao}")
            continue
        fim_anterior = m.offset + m.error_length

        if separada:
            motivo, automatica = "Palavras grudadas: faltava um espaço.", True
        else:
            motivo = m.message
            alternativas = [r for r in m.replacements if r.lower() != corrigido.lower()][:2]
            if alternativas:
                motivo += f" (alternativas: {', '.join(alternativas)})"
            automatica = not _e_sugestao(m)
            if automatica and _distancia(trecho, corrigido) > DISTANCIA_MAXIMA_AUTOMATICA:
                motivo += " Sugestão muito diferente do original: confira antes de aceitar."
                automatica = False
        correcao = {
            "offset": m.offset,
            "tamanho": m.error_length,
            "original": trecho,
            "corrigido": corrigido,
            "motivo": motivo,
            "tipo": "automatica" if automatica else "sugestao",
            "aceita": automatica,
        }
        # "decasa" → "década" ou "de casa"? O LanguageTool põe a versão com espaço no fim
        # da lista e só o contexto diz qual é a certa: o autor escolhe.
        com_espaco = None if separada else _versao_com_espaco(trecho, m.replacements)
        # Correção só de acento ("labios" → "lábios") não deixa dúvida.
        if com_espaco and com_espaco.lower() != corrigido.lower() and _distancia(trecho, corrigido) > 0:
            correcao.update(
                motivo="Pode ser erro de digitação ou palavras grudadas: escolha a certa.",
                tipo="sugestao",
                aceita=False,
                opcoes=[corrigido, com_espaco],
            )
        correcoes.append(correcao)

    correcoes.sort(key=lambda c: c["offset"])
    return Resultado(
        texto_corrigido=aplicar(texto, correcoes),
        correcoes=correcoes,
        observacoes="\n".join(f"- {o}" for o in observacoes),
    )
