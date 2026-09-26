import re
from types import SimpleNamespace

import corretor
from corretor import _distancia, _sugestao, corrigir


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


# --- sugestões absurdas e palavras grudadas -----------------------------------------


class _LTFalso:
    """Corretor ortográfico mínimo: marca toda palavra fora do vocabulário."""

    def __init__(self, vocabulario, sugestoes):
        self.vocabulario, self.sugestoes = vocabulario, sugestoes

    def check(self, texto):
        return [
            SimpleNamespace(
                offset=p.start(),
                error_length=len(p.group()),
                replacements=self.sugestoes.get(p.group(), []),
                message="Possível erro de ortografia.",
                rule_id="MORFOLOGIK_RULE_PT_BR",
                category="TYPOS",
                rule_issue_type="misspelling",
            )
            for p in re.finditer(r"\w+", texto)
            if p.group().lower() not in self.vocabulario
        ]


def _usar(monkeypatch, vocabulario, sugestoes):
    monkeypatch.setattr(corretor, "_get_tool", lambda: _LTFalso(vocabulario, sugestoes))


def test_distancia_ignora_acentos_e_conta_letras_trocadas_de_lugar_como_um_erro():
    assert _distancia("nao", "não") == 0
    assert _distancia("evradde", "verdade") == 2
    assert _distancia("noslençois", "moquencos") > 2


def test_sugestao_muito_diferente_vira_checkbox(monkeypatch):
    _usar(monkeypatch, {"ele", "viu"}, {"Rhyssa": ["Chica"]})
    r = corrigir("Ele viu Rhyssa.")
    assert r.texto_corrigido == "Ele viu Rhyssa."
    [c] = r.correcoes
    assert (c["corrigido"], c["tipo"], c["aceita"]) == ("Chica", "sugestao", False)


def test_sugestao_parecida_continua_automatica(monkeypatch):
    _usar(monkeypatch, {"ele", "sabia"}, {"nao": ["não"]})
    assert corrigir("Ele nao sabia.").texto_corrigido == "Ele não sabia."


def test_separa_palavras_grudadas_e_corrige_as_partes(monkeypatch):
    _usar(
        monkeypatch,
        {"ela", "deitou", "nos", "no", "limpos"},
        {"noslençois": ["moquencos"], "lençois": ["lençóis"], "slençois": ["lençóis"]},
    )
    r = corrigir("Ela deitou noslençois limpos.")
    assert r.texto_corrigido == "Ela deitou nos lençóis limpos."
    [c] = r.correcoes
    assert (c["original"], c["corrigido"], c["tipo"]) == ("noslençois", "nos lençóis", "automatica")


def test_separa_palavra_grudada_mesmo_sem_sugestao_do_languagetool(monkeypatch):
    _usar(monkeypatch, {"ele", "saiu", "de", "casa"}, {})
    assert corrigir("Ele saiu decasa.").texto_corrigido == "Ele saiu de casa."


def test_nao_separa_quando_a_sugestao_do_languagetool_e_boa(monkeypatch):
    _usar(monkeypatch, {"ele", "ficou", "em", "da", "mesa"}, {"embaico": ["embaixo"], "baico": ["baixo"]})
    assert corrigir("Ele ficou embaico da mesa.").texto_corrigido == "Ele ficou embaixo da mesa."


def test_nao_separa_quando_a_segunda_parte_precisaria_de_correcao(monkeypatch):
    # "mome" existe e "ntum" → "num" está a uma letra: separar inventaria "mome num".
    _usar(monkeypatch, {"era", "mome", "num"}, {"momentum": ["monentelo"], "ntum": ["num"]})
    r = corrigir("Era momentum.")
    assert r.texto_corrigido == "Era momentum."
    [c] = r.correcoes
    assert (c["corrigido"], c["tipo"]) == ("monentelo", "sugestao")


def test_na_duvida_entre_corrigir_e_separar_o_autor_escolhe(monkeypatch):
    # "decasa" → "década" ou "de casa"? "embaico" → "embaixo" ou "em baico"? Só o contexto diz.
    _usar(monkeypatch, {"ele", "saiu", "cedo"}, {"decasa": ["década", "dessas", "de casa", "decas a"]})
    r = corrigir("Ele saiu decasa cedo.")
    assert r.texto_corrigido == "Ele saiu decasa cedo."
    [c] = r.correcoes
    assert (c["tipo"], c["aceita"], c["opcoes"]) == ("sugestao", False, ["década", "de casa"])


def test_sugestao_que_so_insere_espaco_em_primeiro_continua_automatica(monkeypatch):
    _usar(monkeypatch, {"caiu"}, {"Derrepente": ["De repente"]})
    assert corrigir("Derrepente caiu.").texto_corrigido == "De repente caiu."


def test_versoes_com_espaco_sem_sentido_nao_geram_duvida(monkeypatch):
    # O LanguageTool acrescenta separações absurdas ao fim da lista para muitas palavras.
    _usar(
        monkeypatch,
        {"a", "de"},
        {
            "temperatira": ["temperatura", "tempera tira"],
            "querod": ["quero", "quero d"],
            "dque": ["que", "d que"],
            "labios": ["lábios", "la bios"],
        },
    )
    r = corrigir("temperatira querod dque labios")
    assert r.texto_corrigido == "temperatura quero que lábios"
    assert all(c["tipo"] == "automatica" for c in r.correcoes)


def test_correcao_so_de_acento_nao_gera_duvida(monkeypatch):
    _usar(monkeypatch, {"se"}, {"sera": ["será", "se ra"]})
    [c] = corrigir("sera").correcoes
    assert (c["corrigido"], c["tipo"]) == ("será", "automatica")


def test_separacao_com_palavra_de_uma_letra_nao_gera_duvida(monkeypatch):
    _usar(monkeypatch, set(), {"apra": ["para", "a pra"]})
    assert corrigir("apra").texto_corrigido == "para"
