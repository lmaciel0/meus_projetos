"""Revisão com IA local (Ollama), como alternativa ao LanguageTool.

A IA devolve cada parágrafo corrigido; as diferenças viram sugestões com checkbox, nunca
são aplicadas sozinhas: nos testes ela às vezes muda o sentido ("ele e a Kessa" → "ele é a
Kessa") ou reescreve ("não mereço oc]e" → "não mereço isso").
"""

import difflib
import json
import os
import re
import urllib.error
import urllib.request
from collections.abc import Callable

import analise
from corretor import (
    REGRA_DIALOGO,
    ErroCorrecao,
    Resultado,
    _correcoes_fixas,
    _dialogos,
    _paragrafos,
    aplicar,
)

URL = os.environ.get("CORRETOR_OLLAMA_URL", "http://localhost:11434")
MODELO = os.environ.get("CORRETOR_MODELO_IA", "gemma4:e4b-it-qat")
# Muda quando as instruções mudam, para não reaproveitar revisões feitas com as antigas.
VERSAO_INSTRUCOES = 2
# Parágrafos vão em blocos: a IA ganha contexto ("galou" → "falou" só com a frase anterior)
# e o tempo de ler as instruções (~20 s sem placa de vídeo) é pago uma vez por bloco.
PALAVRAS_POR_BLOCO = 150
MOTIVO_IA = "Sugestão da IA"
REGRA_IA = "IA"
# Medido num notebook sem placa de vídeo (i5 de 11ª geração): ~0,8 s por palavra.
SEGUNDOS_POR_PALAVRA = 0.8
CONTEXTO = 30  # caracteres de cada lado mostrados junto com a sugestão

INSTRUCOES = (
    "Você é um revisor de textos de ficção em português do Brasil. Corrija somente erros: digitação, "
    "ortografia, acentuação, palavras grudadas ou separadas por engano, pontuação, crase, concordância e "
    "regência. Preserve a voz do autor: não troque palavras certas por sinônimos, não reescreva frases, não "
    "acrescente nem remova frases e não mude gírias e marcas de oralidade (como \"pra\", \"pro\", \"tá\"). "
    "Não mude o sentido: se não der para saber qual palavra o autor quis, deixe como está. Em diálogos, depois "
    "do travessão o verbo que indica quem fala fica em minúscula (— Vem? — perguntou ele). "
    "O texto pode ter vários parágrafos separados por linha em branco: mantenha exatamente a mesma divisão, "
    "sem juntar nem separar parágrafos. Responda apenas com o texto corrigido, sem comentários, aspas ou explicações."
)

# Marcas de oralidade que a IA às vezes "corrige" apesar das instruções.
# Só a troca pela forma formal é barrada: "pro" → "por" é erro de digitação e passa.
ORALIDADE = {
    "pra": ("para",),
    "pras": ("para as",),
    "pro": ("para o", "para"),
    "pros": ("para os",),
    "tá": ("está",),
    "tô": ("estou",),
    "né": ("não é",),
    "cê": ("você",),
}

_TOKEN = re.compile(r"\s+|\S+")


class Cache:
    """Revisões já feitas, para retomar um texto longo de onde parou. Padrão: só na memória."""

    def __init__(self):
        self._dados: dict[tuple[str, str], str] = {}

    def ler_revisao_ia(self, modelo: str, paragrafo: str) -> str | None:
        return self._dados.get((modelo, paragrafo))

    def gravar_revisao_ia(self, modelo: str, paragrafo: str, revisado: str) -> None:
        self._dados[(modelo, paragrafo)] = revisado


def _pedir(caminho: str, corpo: dict | None = None, timeout: float = 5) -> dict:
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(f"{URL}{caminho}", dados, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resposta:
        return json.load(resposta)


def disponivel() -> tuple[bool, str]:
    """Se o Ollama está rodando e tem o modelo. Retorna (ok, explicação para o autor)."""
    try:
        modelos = {m["name"] for m in _pedir("/api/tags").get("models", [])}
    except (urllib.error.URLError, OSError, ValueError):
        return False, "O Ollama não está rodando. Abra o aplicativo do Ollama e recarregue a página."
    if MODELO not in modelos:
        return False, f"O modelo {MODELO} não está instalado. Rode no terminal: ollama pull {MODELO}"
    return True, f"Ollama com {MODELO}"


def _chamar(paragrafo: str, nomes: list[str]) -> str:
    instrucoes = INSTRUCOES
    if nomes:
        instrucoes += f" Nomes próprios e termos da história, que não devem ser alterados: {', '.join(nomes)}."
    corpo = {
        "model": MODELO,
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_ctx": 4096},
        "messages": [{"role": "system", "content": instrucoes}, {"role": "user", "content": paragrafo}],
    }
    try:
        return _pedir("/api/chat", corpo, timeout=900)["message"]["content"]
    except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
        raise ErroCorrecao(f"Erro ao falar com a IA (Ollama): {e}") from e


def _sem_moldura(resposta: str) -> str:
    """Tira o bloco de código em volta, que alguns modelos acrescentam."""
    return re.sub(r"^```\w*\n?|\n?```$", "", resposta.strip()).strip()


def _limpar(resposta: str, paragrafo: str) -> str | None:
    """A resposta da IA, ou None se ela não parece uma revisão do parágrafo."""
    texto = _sem_moldura(resposta)
    # Aspas em volta de tudo, que o parágrafo original não tinha.
    if len(texto) > 1 and (texto[0], texto[-1]) in (('"', '"'), ("“", "”")) and paragrafo.strip()[:1] != texto[0]:
        texto = texto[1:-1].strip()
    if not texto:
        return None
    # Comentário ou reescrita em vez de revisão: tamanho muito diferente do original.
    proporcao = len(texto) / max(len(paragrafo.strip()), 1)
    if not 0.6 <= proporcao <= 1.6 or texto.count("\n") > paragrafo.count("\n"):
        return None
    # Mantém os espaços de início e fim do parágrafo original.
    inicio = paragrafo[: len(paragrafo) - len(paragrafo.lstrip())]
    fim = paragrafo[len(paragrafo.rstrip()) :]
    return inicio + texto + fim


def diferencas(original: str, revisado: str) -> list[tuple[int, int, str]]:
    """Trechos alterados, como (início, fim, novo texto) no original, sempre em palavras inteiras.

    O texto é comparado em blocos sem espaço (palavra com a pontuação grudada), então
    "loucura as não" → "loucura, mas não" vira um trecho só ("loucura as" → "loucura, mas").
    """
    a, b = _TOKEN.findall(original), _TOKEN.findall(revisado)
    blocos = [
        [i1, i2, j1, j2]
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
        if tag != "equal"
    ]

    def precisa_estender(bloco):
        i1, i2, j1, j2 = bloco
        return i1 == i2 or j1 == j2 or any(t.isspace() for t in (a[i1], a[i2 - 1], b[j1], b[j2 - 1]))

    def so_pontuacao(bloco):
        # "frio" → "frio," com ",mas" → "mas": a vírgula mudou de lugar, as duas trocas andam juntas.
        i1, i2, j1, j2 = bloco
        return re.sub(r"\W", "", "".join(a[i1:i2])) == re.sub(r"\W", "", "".join(b[j1:j2]))

    def juntar(blocos):
        # Trechos que se sobrepõem viram um. Palavras vizinhas trocadas ficam separadas, para
        # o autor aceitar uma sem a outra; só se junta pelo espaço a troca de pontuação e o
        # trecho que vai ser estendido (senão avançaria sobre o vizinho). Entre dois blocos o texto é igual
        # nos dois lados, então as faixas andam juntas.
        juntos = []
        for bloco in blocos:
            so_espaco = all(t.isspace() for t in a[juntos[-1][1] : bloco[0]]) if juntos else False
            if juntos and (
                bloco[0] <= juntos[-1][1]
                or (so_espaco and any(f(x) for f in (precisa_estender, so_pontuacao) for x in (juntos[-1], bloco)))
            ):
                juntos[-1][1], juntos[-1][3] = max(juntos[-1][1], bloco[1]), max(juntos[-1][3], bloco[3])
            else:
                juntos.append(bloco)
        return juntos

    blocos = juntar(blocos)
    for bloco in blocos:
        i1, i2, j1, j2 = bloco
        # Troca só de espaço, inserção ou remoção: inclui a palavra vizinha para ficar legível.
        while i1 > 0 and (i1 == i2 or j1 == j2 or a[i1].isspace() or b[j1].isspace()):
            i1, j1 = i1 - 1, j1 - 1
        while i2 < len(a) and (a[i2 - 1].isspace() or b[j2 - 1].isspace()):
            i2, j2 = i2 + 1, j2 + 1
        if i1 == i2 and i2 < len(a):  # inserção no começo do texto
            i2, j2 = i2 + 1, j2 + 1
        bloco[:] = [i1, i2, j1, j2]
    blocos = juntar(blocos)

    inicios = [0]
    for t in a:
        inicios.append(inicios[-1] + len(t))
    return [(inicios[i1], inicios[i2], "".join(b[j1:j2])) for i1, i2, j1, j2 in blocos]


def _blocos(paragrafos: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    """Parágrafos seguidos, até PALAVRAS_POR_BLOCO palavras por bloco."""
    blocos, atual, palavras = [], [], 0
    for item in paragrafos:
        n = len(item[1].split())
        if atual and palavras + n > PALAVRAS_POR_BLOCO:
            blocos.append(atual)
            atual, palavras = [], 0
        atual.append(item)
        palavras += n
    if atual:
        blocos.append(atual)
    return blocos


def _revisar_bloco(paragrafos: list[str], nomes: list[str]) -> list[str | None]:
    """Revisão de cada parágrafo. Vários vão numa chamada só: a IA ganha contexto e o
    tempo de ler as instruções é pago uma vez. Se ela juntar ou separar parágrafos, cada
    um é revisado sozinho."""
    if len(paragrafos) > 1:
        resposta = _sem_moldura(_chamar("\n\n".join(p.strip() for p in paragrafos), nomes))
        partes = [p for p in re.split(r"\n[ \t]*\n", resposta) if p.strip()]
        if len(partes) == len(paragrafos):
            return [_limpar(parte, p) for parte, p in zip(partes, paragrafos)]
    return [_limpar(_chamar(p, nomes), p) for p in paragrafos]


def revisar(
    texto: str,
    nomes: list[str],
    cache=None,
    progresso: Callable[[int, int], None] | None = None,
) -> tuple[list[dict], int]:
    """Sugestões da IA para o texto, em blocos de parágrafos. Retorna (sugestões, parágrafos sem revisão)."""
    cache = cache or Cache()
    chave_modelo = f"{MODELO}#{VERSAO_INSTRUCOES}"
    blocos = _blocos(_paragrafos(texto))
    sugestoes, falhas = [], 0
    for n, bloco in enumerate(blocos, start=1):
        revisados = {p: cache.ler_revisao_ia(chave_modelo, p) for _, p in bloco}
        pendentes = list(dict.fromkeys(p for p, r in revisados.items() if r is None))
        if pendentes:
            for p, r in zip(pendentes, _revisar_bloco(pendentes, nomes)):
                revisados[p] = r
                if r is None:
                    falhas += 1
                else:
                    cache.gravar_revisao_ia(chave_modelo, p, r)
        for inicio, paragrafo in bloco:
            for comeco, fim, novo in diferencas(paragrafo, revisados[paragrafo] or paragrafo):
                original = paragrafo[comeco:fim]
                # Um pedaço da frase em volta: "e" → "é" sozinho não diz nada.
                antes = paragrafo[max(0, comeco - CONTEXTO) : comeco]
                depois = paragrafo[fim : fim + CONTEXTO]
                sugestoes.append(
                    {
                        "contexto": ("…" if comeco > CONTEXTO else "") + antes + "**" + original + "**" + depois
                        + ("…" if fim + CONTEXTO < len(paragrafo) else ""),
                        "offset": inicio + comeco,
                        "tamanho": fim - comeco,
                        "original": original,
                        "corrigido": novo,
                        "motivo": MOTIVO_IA,
                        "regra": REGRA_IA,
                        "tipo": "sugestao",
                        "aceita": False,
                    }
                )
        if progresso:
            progresso(n, len(blocos))
    return sugestoes, falhas


def _mexe_no_que_deve_ficar(sugestao: dict, ignoradas: set[str]) -> bool:
    """Trocas de nomes do dicionário ou de marcas de oralidade pela forma formal ("pra" → "para")."""
    antes = {p.lower() for p in re.findall(r"\w+", sugestao["original"])}
    depois = {p.lower() for p in re.findall(r"\w+", sugestao["corrigido"])}
    removidas = antes - depois
    if removidas & ignoradas:
        return True
    corrigido = f" {' '.join(re.findall(r'\w+', sugestao['corrigido'].lower()))} "
    return any(f" {forma} " in corrigido for p in removidas for forma in ORALIDADE.get(p, ()))


def corrigir_com_ia(
    texto: str,
    ignoradas: set[str] = frozenset(),
    fixas: dict[str, str] | None = None,
    regras_desligadas: set[str] = frozenset(),
    progresso: Callable[[int, int], None] | None = None,
    cache=None,
) -> tuple[Resultado, int]:
    """Como corretor.corrigir, mas com a IA no lugar do LanguageTool. Retorna (resultado, falhas)."""
    correcoes = _correcoes_fixas(texto, fixas or {})
    if REGRA_DIALOGO not in regras_desligadas:
        correcoes += _dialogos(texto)
    faixas = [(c["offset"], c["offset"] + c["tamanho"]) for c in correcoes]

    nomes = sorted({p[:1].upper() + p[1:] for p in ignoradas})
    sugestoes, falhas = revisar(texto, nomes, cache, progresso)
    for s in sugestoes:
        fim = s["offset"] + s["tamanho"]
        # O dicionário pessoal e os travessões têm prioridade, como no LanguageTool.
        if any(s["offset"] < f and i < fim for i, f in faixas) or _mexe_no_que_deve_ficar(s, set(ignoradas)):
            continue
        correcoes.append(s)

    observacoes = []
    if analise.REGRA_REPETICAO not in regras_desligadas:
        observacoes += analise.repeticoes(texto, ignoradas)
    correcoes.sort(key=lambda c: c["offset"])
    observacoes.sort(key=lambda o: o["offset"])
    resultado = Resultado(texto_corrigido=aplicar(texto, correcoes), correcoes=correcoes, observacoes=observacoes)
    return resultado, falhas


def estimativa_minutos(texto: str) -> int:
    return max(1, round(len(texto.split()) * SEGUNDOS_POR_PALAVRA / 60))
