"""Verificações próprias para ficção, que o LanguageTool não faz: repetições, nomes e estatísticas."""

import re
from collections import Counter

REGRA_REPETICAO = "REPETICAO_PROXIMA"
REGRA_NOME = "NOME_PARECIDO"

# Palavras que se repetem naturalmente e não interessam nas repetições nem nas mais usadas.
# Só as de 4 letras ou mais: as menores já são ignoradas pelo tamanho.
PALAVRAS_COMUNS = {
    "para", "pela", "pelo", "pelas", "pelos", "como", "mais", "mesmo", "mesma", "mesmos", "mesmas",
    "ainda", "quando", "onde", "então", "depois", "antes", "sobre", "entre", "também", "muito",
    "muita", "muitos", "muitas", "porque", "isso", "isto", "aquilo", "aquele", "aquela", "aqueles",
    "aquelas", "esse", "essa", "esses", "essas", "este", "esta", "estes", "estas", "eles", "elas",
    "dele", "dela", "deles", "delas", "nosso", "nossa", "nossos", "nossas", "minha", "minhas", "meus",
    "seus", "suas", "você", "vocês", "estava", "estavam", "estou", "está", "estão", "eram", "foram",
    "sido", "tinha", "tinham", "tenho", "havia", "seria", "será", "pode", "podia", "fazer", "feito",
    "nada", "tudo", "todo", "toda", "todos", "todas", "algo", "alguém", "outro", "outra", "outros",
    "outras", "cada", "qual", "quem", "assim", "agora", "apenas", "sempre", "nunca", "aqui", "lhes",
    "numa", "nuns", "numas", "umas", "desse", "dessa", "deste", "desta", "nesse", "nessa", "neste",
    "nesta", "naquele", "naquela", "disse", "quanto", "estar", "vezes", "pois", "porém", "contudo",
    "embora", "enquanto", "tão", "até", "sem", "já", "não", "sim", "lá", "cá", "vai", "vou", "foi",
}

JANELA_REPETICAO = 15  # palavras
TAMANHO_MINIMO = 4

_PALAVRA = re.compile(r"[^\W\d_]+")
# Nome no meio da frase: maiúscula logo depois de outra palavra, vírgula ou ponto e vírgula.
_NOME_NO_MEIO = re.compile(r"(?<=[\w,;]\s)[A-ZÀ-Ý][^\W\d_]+")
_CAPITALIZADA = re.compile(r"(?<![\w])[A-ZÀ-Ý][^\W\d_]+")


def _relevante(palavra: str, ignoradas: set[str]) -> bool:
    chave = palavra.lower()
    return len(chave) >= TAMANHO_MINIMO and chave not in PALAVRAS_COMUNS and chave not in ignoradas


def repeticoes(texto: str, ignoradas: set[str] = frozenset()) -> list[dict]:
    """A mesma palavra de novo a menos de JANELA_REPETICAO palavras de distância."""
    observacoes, ultima = [], {}
    for i, achado in enumerate(_PALAVRA.finditer(texto)):
        palavra = achado.group()
        # Com maiúscula costuma ser nome de personagem, que se repete naturalmente.
        if not _relevante(palavra, ignoradas) or palavra[0].isupper():
            continue
        chave = palavra.lower()
        anterior = ultima.get(chave)
        if anterior is not None and i - anterior <= JANELA_REPETICAO:
            observacoes.append(
                {
                    "trecho": palavra,
                    "mensagem": f"Repetida {i - anterior} palavras depois da anterior. É intencional?",
                    "sugestao": None,
                    "offset": achado.start(),
                    "tamanho": len(palavra),
                    "regra": REGRA_REPETICAO,
                    "tipo": "repeticao",
                }
            )
        ultima[chave] = i
    return observacoes


def nomes_parecidos(
    texto: str, ignoradas: set[str] = frozenset(), desconhecidas: set[str] | None = None
) -> list[dict]:
    """ "Aelyn" num texto em que o nome é "Aelin": grafias de um nome que diferem em uma letra.

    Conta como nome a palavra com maiúscula que aparece ao menos duas vezes no meio da frase,
    ou duas vezes em qualquer lugar sendo desconhecida do corretor ortográfico (nomes
    inventados sempre são), ou que está nas palavras aceitas do dicionário pessoal.
    `desconhecidas`: palavras que o corretor ortográfico marcou; se dado, só elas podem ser
    a variante, o que evita confundir "Estava" com "Estavam".
    """
    from corretor import _distancia  # evita import circular

    no_meio = Counter(m.group() for m in _NOME_NO_MEIO.finditer(texto))
    todas = Counter(m.group() for m in _CAPITALIZADA.finditer(texto))
    nomes = {n for n, vezes in no_meio.items() if vezes >= 2 and len(n) >= TAMANHO_MINIMO}
    nomes |= {n for n in desconhecidas or () if todas[n] >= 2 and len(n) >= TAMANHO_MINIMO}
    nomes |= {p[:1].upper() + p[1:] for p in ignoradas if len(p) >= TAMANHO_MINIMO and p.isalpha()}

    trocas: dict[str, str] = {}
    for variante, vezes in todas.items():
        if len(variante) < TAMANHO_MINIMO or variante.lower() in ignoradas:
            continue
        if desconhecidas is not None and variante not in desconhecidas:
            continue
        candidatos = [
            n
            for n in nomes
            if n != variante
            and _distancia(n, variante) == 1
            and (n.lower() in ignoradas or todas[n] > vezes)
        ]
        if candidatos:
            trocas[variante] = max(candidatos, key=lambda n: (n.lower() in ignoradas, todas[n]))

    observacoes = []
    for achado in _CAPITALIZADA.finditer(texto):
        nome = trocas.get(achado.group())
        if nome:
            observacoes.append(
                {
                    "trecho": achado.group(),
                    "mensagem": f"Nome escrito de outro jeito? No resto do texto aparece “{nome}”.",
                    "sugestao": nome,
                    "offset": achado.start(),
                    "tamanho": len(achado.group()),
                    "regra": REGRA_NOME,
                    "tipo": "consistencia",
                }
            )
    return observacoes


def estatisticas(texto: str, ignoradas: set[str] = frozenset(), quantas: int = 10) -> dict:
    palavras = _PALAVRA.findall(texto)
    frequencia = Counter(p.lower() for p in palavras if _relevante(p, ignoradas))
    paragrafos = [p for p in re.split(r"\n\s*\n|\n", texto) if p.strip()]
    return {
        "palavras": len(palavras),
        "paragrafos": len(paragrafos),
        "mais_usadas": frequencia.most_common(quantas),
    }
