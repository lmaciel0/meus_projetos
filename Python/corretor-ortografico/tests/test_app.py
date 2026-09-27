"""Testes da interface: rodam o app.py de verdade com um LanguageTool falso e banco temporário."""

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

import corretor
import db

APP = str(Path(__file__).parent.parent / "app.py")


VOCABULARIO = {"ele", "ela", "nós", "viu", "sabia", "sabíamos", "a", "irmã", "como", "não", "chica"}
SUGESTOES = {"nao": ["não"], "Rhyssa": ["Chica"]}


class _LTFalso:
    """Marca palavras fora do vocabulário (com sugestões para "nao" e "Rhyssa") e "tipo" como estilo."""

    def check(self, texto):
        achados = []
        for m in re.finditer(r"\w+", texto):
            palavra = m.group()
            base = dict(offset=m.start(), error_length=len(palavra))
            if palavra == "tipo":
                achados.append(
                    SimpleNamespace(**base, replacements=["como"], message="Coloquialismo.", rule_id="TIPO_COLOQUIAL",
                                    category="COLLOQUIALISMS", rule_issue_type="style")
                )
            elif palavra.lower() not in VOCABULARIO:
                achados.append(
                    SimpleNamespace(**base, replacements=SUGESTOES.get(palavra, []), message="Possível erro.",
                                    rule_id="MORFOLOGIK_RULE_PT_BR", category="TYPOS", rule_issue_type="misspelling")
                )
        return achados


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "historico.db")
    monkeypatch.setattr(corretor, "_get_tool", lambda: _LTFalso())
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    return at


def _botao(at, rotulo):
    return next(b for b in at.button if b.label == rotulo)


def _corrigido(at):
    return next(t for t in at.text_area if t.key and t.key.startswith("corr_edit_"))


def _corrigir(at, texto):
    at.text_area[0].input(texto)
    _botao(at, "Corrigir texto").click()
    at.run()
    assert not at.exception, at.exception


def test_corrige_texto_colado_e_salva_no_historico(app):
    _corrigir(app, "Ele nao viu Rhyssa.")
    assert _corrigido(app).value == "Ele não viu Rhyssa."
    [registro] = db.listar()
    assert registro["texto_corrigido"] == "Ele não viu Rhyssa."


def test_aceitar_sugestao_atualiza_texto_e_banco(app):
    _corrigir(app, "Ele nao viu Rhyssa.")
    [sugestao] = [c for c in app.checkbox if c.key and c.key.startswith("sug_")]
    sugestao.check()
    app.run()
    assert _corrigido(app).value == "Ele não viu Chica."
    assert db.listar()[0]["texto_corrigido"] == "Ele não viu Chica."


def test_edicao_manual_e_salva_e_trava_as_decisoes(app):
    _corrigir(app, "Ele nao viu Rhyssa.")
    _corrigido(app).input("Ele não viu Rhyssa, a irmã.")
    _botao(app, "Salvar edição").click()
    app.run()
    assert db.listar()[0]["texto_final"] == "Ele não viu Rhyssa, a irmã."
    assert _corrigido(app).value == "Ele não viu Rhyssa, a irmã."
    [sugestao] = [c for c in app.checkbox if c.key and c.key.startswith("sug_")]
    assert sugestao.disabled

    _botao(app, "Descartar edição").click()
    app.run()
    assert db.listar()[0]["texto_final"] == ""
    assert _corrigido(app).value == "Ele não viu Rhyssa."


def test_aplicar_e_silenciar_observacao(app):
    _corrigir(app, "Ele tipo sabia.")
    _botao(app, "Aplicar").click()
    app.run()
    assert _corrigido(app).value == "Ele como sabia."

    _corrigir(app, "Ela tipo sabia.")
    _botao(app, "Silenciar").click()
    app.run()
    assert "TIPO_COLOQUIAL" in db.listar_regras()
    _corrigir(app, "Nós tipo sabíamos.")
    assert all(b.label != "Silenciar" for b in app.button)


def test_excluir_do_historico_pede_confirmacao(app):
    _corrigir(app, "Ele nao viu.")
    _botao(app, "Excluir").click()
    app.run()
    assert db.contar() == 1
    _botao(app, "Cancelar").click()
    app.run()
    assert db.contar() == 1
    _botao(app, "Excluir").click()
    app.run()
    _botao(app, "Sim, excluir").click()
    app.run()
    assert db.contar() == 0


def test_dicionario_adiciona_palavra(app):
    campo = next(t for t in app.text_input if t.label == "Palavra ou trecho")
    campo.input("Aelin")
    next(b for b in app.button if b.label == "Adicionar").click()
    app.run()
    assert db.listar_ignoradas() == ["aelin"]


def test_aplicar_nome_no_lugar_de_sugestao_recusada(app):
    SUGESTOES["Rhissa"] = ["Chica"]
    try:
        _corrigir(app, "Rhyssa viu. Rhyssa viu. Rhissa viu.")
    finally:
        del SUGESTOES["Rhissa"]
    _botao(app, "Aplicar").click()
    app.run()
    assert _corrigido(app).value == "Rhyssa viu. Rhyssa viu. Rhyssa viu."
    assert db.listar()[0]["texto_corrigido"] == "Rhyssa viu. Rhyssa viu. Rhyssa viu."
