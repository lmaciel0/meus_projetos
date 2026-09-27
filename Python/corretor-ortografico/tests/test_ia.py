import pytest

import ia
from corretor import ErroCorrecao


def _trechos(original, revisado):
    return [(original[i:f], novo) for i, f, novo in ia.diferencas(original, revisado)]


@pytest.mark.parametrize(
    "original, revisado, esperado",
    [
        ("parece loucura as não é", "parece loucura, mas não é", [("loucura as", "loucura, mas")]),
        ("frio ,mas ão como", "frio, mas não como", [("frio ,mas ão", "frio, mas não")]),
        ("não consigo  nem", "não consigo nem", [("consigo  nem", "consigo nem")]),
        ("Mas.. mas eu", "Mas... mas eu", [("Mas..", "Mas...")]),
        ("tirando meusvaelos do", "tirando meus cabelos do", [("meusvaelos", "meus cabelos")]),
        ("Ei e apaixonei pro voc~e e", "Eu me apaixonei por você e", [("Ei", "Eu"), ("e", "me"), ("pro", "por"), ("voc~e", "você")]),
        ("vai ser os proximos", "vão ser os próximos", [("vai", "vão"), ("proximos", "próximos")]),
        ("igual", "igual", []),
    ],
)
def test_diferencas_em_palavras_inteiras(original, revisado, esperado):
    assert _trechos(original, revisado) == esperado


def test_diferencas_aplicadas_refazem_o_texto_revisado():
    original, revisado = "Ei e apaixonei, pro voc~e.  Fim", "Eu me apaixonei por você. Fim."
    texto = original
    for inicio, fim, novo in reversed(ia.diferencas(original, revisado)):
        texto = texto[:inicio] + novo + texto[fim:]
    assert texto == revisado


@pytest.mark.parametrize(
    "resposta, esperado",
    [
        ("Ele não viu.", "Ele não viu."),
        ("```\nEle não viu.\n```", "Ele não viu."),
        ("“Ele não viu.”", "Ele não viu."),
        ("", None),
        ("Aqui está o texto corrigido, com as alterações explicadas abaixo: Ele não viu. Mudei nao para não.", None),
    ],
)
def test_limpa_resposta_e_descarta_o_que_nao_e_revisao(resposta, esperado):
    assert ia._limpar(resposta, "Ele nao viu.") == esperado


def _ia(monkeypatch, respostas):
    chamadas = []

    def chamar(paragrafo, nomes):
        chamadas.append((paragrafo, nomes))
        return respostas.get(paragrafo, paragrafo)

    monkeypatch.setattr(ia, "_chamar", chamar)
    return chamadas


def test_sugestoes_por_paragrafo_com_offsets_e_contexto(monkeypatch):
    _ia(monkeypatch, {"Ela sabia.\n\n— Vem? — Perguntou ele.": "Ela sabia.\n\n— Vem? — perguntou ele."})
    texto = "Ela sabia.\n— Vem? — Perguntou ele."
    sugestoes, falhas = ia.revisar(texto, [])
    [s] = sugestoes
    assert falhas == 0
    assert texto[s["offset"] : s["offset"] + s["tamanho"]] == "Perguntou"
    assert (s["corrigido"], s["tipo"], s["aceita"]) == ("perguntou", "sugestao", False)
    assert s["contexto"] == "— Vem? — **Perguntou** ele."


def test_cache_evita_chamar_a_ia_de_novo(monkeypatch):
    chamadas = _ia(monkeypatch, {"Ele nao viu.": "Ele não viu."})
    cache = ia.Cache()
    ia.revisar("Ele nao viu.", [], cache)
    sugestoes, _ = ia.revisar("Ele nao viu.", [], cache)
    assert len(chamadas) == 1 and sugestoes[0]["corrigido"] == "não"


def test_resposta_ruim_conta_como_falha_e_nao_gera_sugestao(monkeypatch):
    _ia(monkeypatch, {"Ele nao viu.": ""})
    assert ia.revisar("Ele nao viu.", []) == ([], 1)


def test_corrigir_com_ia_respeita_dicionario_oralidade_e_travessao(monkeypatch):
    texto = "- Aelin tava pra casa nao."
    chamadas = _ia(monkeypatch, {texto: "— Aline estava para casa não."})
    resultado, falhas = ia.corrigir_com_ia(texto, ignoradas={"aelin"}, fixas={"tava": "estava"})
    por_original = {c["original"]: c for c in resultado.correcoes}
    # Travessão e correção fixa são automáticos; a IA não pode trocar o nome nem o "pra".
    assert por_original["-"]["aceita"] and por_original["tava"]["aceita"]
    assert "Aelin" not in por_original and "pra" not in por_original
    assert por_original["nao."]["corrigido"] == "não." and not por_original["nao."]["aceita"]
    assert resultado.texto_corrigido == "— Aelin estava pra casa nao."
    assert chamadas[0][1] == ["Aelin"]
    assert falhas == 0


def test_erro_de_conexao_vira_mensagem_amigavel(monkeypatch):
    monkeypatch.setattr(ia, "URL", "http://127.0.0.1:9")
    with pytest.raises(ErroCorrecao, match="Ollama"):
        ia._chamar("Oi.", [])
    assert ia.disponivel()[0] is False


def test_paragrafos_vao_juntos_num_bloco(monkeypatch):
    chamadas = _ia(monkeypatch, {"Ele nao viu.\n\nEla sabia.": "Ele não viu.\n\nEla sabia."})
    sugestoes, falhas = ia.revisar("Ele nao viu.\nEla sabia.", [])
    assert len(chamadas) == 1 and falhas == 0
    assert [(s["original"], s["corrigido"]) for s in sugestoes] == [("nao", "não")]


def test_bloco_com_paragrafos_juntados_e_revisado_um_a_um(monkeypatch):
    chamadas = _ia(
        monkeypatch,
        {"Ele nao viu.\n\nEla sabia.": "Ele não viu. Ela sabia.", "Ele nao viu.": "Ele não viu."},
    )
    sugestoes, _ = ia.revisar("Ele nao viu.\nEla sabia.", [])
    assert [c[0] for c in chamadas] == ["Ele nao viu.\n\nEla sabia.", "Ele nao viu.", "Ela sabia."]
    assert [s["corrigido"] for s in sugestoes] == ["não"]


def test_blocos_respeitam_o_limite_de_palavras(monkeypatch):
    monkeypatch.setattr(ia, "PALAVRAS_POR_BLOCO", 4)
    chamadas = _ia(monkeypatch, {})
    progresso = []
    ia.revisar("Um dois três.\nQuatro cinco.\nSeis.", [], progresso=lambda f, t: progresso.append((f, t)))
    assert [c[0] for c in chamadas] == ["Um dois três.", "Quatro cinco.\n\nSeis."]
    assert progresso == [(1, 2), (2, 2)]


def test_pro_como_erro_de_digitacao_de_por_passa(monkeypatch):
    texto = "Me apaixonei pro você e vou pra casa."
    _ia(monkeypatch, {texto: "Me apaixonei por você e vou para casa."})
    resultado, _ = ia.corrigir_com_ia(texto)
    assert [(c["original"], c["corrigido"]) for c in resultado.correcoes] == [("pro", "por")]
