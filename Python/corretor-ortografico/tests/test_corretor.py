from types import SimpleNamespace

from corretor import _sugestao


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
