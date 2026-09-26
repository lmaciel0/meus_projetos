from types import SimpleNamespace

import corretor
from corretor import _sugestao, corrigir


def _match(replacements, category="TYPOS"):
    return SimpleNamespace(replacements=replacements, category=category)


def test_trecho_com_varias_palavras_preserva_as_que_estavam_certas():
    # O LanguageTool sugere primeiro "um aves", reescrevendo o "uma" que estava certo.
    assert _sugestao("uma ves", _match(["um aves", "uma vez", "uma vês"])) == "uma vez"


def test_trecho_de_uma_palavra_usa_a_primeira_sugestao():
    assert _sugestao("ves", _match(["vez", "vês", "bem"])) == "vez"


def test_sem_sugestao_com_mesmo_numero_de_palavras_usa_a_primeira():
    assert _sugestao("com migo", _match(["comigo", "com mico"])) == "comigo"


def test_empate_mantem_a_ordem_do_languagetool():
    assert _sugestao("uma ves", _match(["uma vez", "uma vês"])) == "uma vez"


# --- dicionário pessoal e correções fixas -----------------------------------------


def _lt(monkeypatch, texto, *marcados):
    """Faz o LanguageTool 'marcar' os trechos dados, com as sugestões dadas."""
    matches = []
    for trecho, sugestoes in marcados:
        offset = texto.index(trecho)
        matches.append(
            SimpleNamespace(
                offset=offset,
                error_length=len(trecho),
                replacements=sugestoes,
                message="Possível erro de ortografia.",
                rule_id="MORFOLOGIK_RULE_PT_BR",
                category="TYPOS",
                rule_issue_type="misspelling",
            )
        )
    monkeypatch.setattr(corretor, "_get_tool", lambda: SimpleNamespace(check=lambda _: matches))


def test_palavra_do_dicionario_pessoal_nao_e_corrigida_nem_observada(monkeypatch):
    texto = "Aelin olhou para Rowan."
    _lt(monkeypatch, texto, ("Aelin", ["Aline"]), ("Rowan", ["Rowa"]))
    r = corrigir(texto, ignoradas={"aelin"})
    assert r.texto_corrigido == "Aelin olhou para Rowa."
    assert [c["original"] for c in r.correcoes] == ["Rowan"]
    assert "Aelin" not in r.observacoes


def test_correcao_fixa_vale_mesmo_sem_o_languagetool_marcar(monkeypatch):
    texto = "Ele tava cansado. Tava mesmo."
    _lt(monkeypatch, texto)
    r = corrigir(texto, fixas={"tava": "estava"})
    assert r.texto_corrigido == "Ele estava cansado. Estava mesmo."
    assert all(c["tipo"] == "automatica" and c["aceita"] for c in r.correcoes)


def test_correcao_fixa_so_pega_palavra_inteira(monkeypatch):
    texto = "A oitava estava vazia."
    _lt(monkeypatch, texto)
    assert corrigir(texto, fixas={"tava": "estava"}).texto_corrigido == texto


def test_correcao_fixa_tem_prioridade_sobre_o_languagetool(monkeypatch):
    texto = "Era uma ves."
    _lt(monkeypatch, texto, ("uma ves", ["um aves"]))
    r = corrigir(texto, fixas={"ves": "vez"})
    assert r.texto_corrigido == "Era uma vez."
    assert len(r.correcoes) == 1
