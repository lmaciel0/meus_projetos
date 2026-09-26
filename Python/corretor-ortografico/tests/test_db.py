import sqlite3

import db


def test_migra_banco_antigo_sem_coluna_arquivo(tmp_path, monkeypatch):
    caminho = tmp_path / "historico.db"
    monkeypatch.setattr(db, "DB_PATH", caminho)
    with sqlite3.connect(caminho) as conn:
        conn.execute(
            """
            CREATE TABLE historico (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                data            TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                texto_original  TEXT NOT NULL,
                texto_corrigido TEXT NOT NULL,
                correcoes       TEXT NOT NULL,
                observacoes     TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.execute("INSERT INTO historico (texto_original, texto_corrigido, correcoes) VALUES ('a', 'a', '[]')")
    conn.close()

    db.inicializar()
    db.inicializar()  # idempotente
    novo = db.salvar("b", "b", [], "", arquivo="conto.pdf")

    assert [r["arquivo"] for r in db.listar()] == ["conto.pdf", ""]
    assert db.obter(novo)["arquivo"] == "conto.pdf"


def test_dicionario_pessoal_e_correcoes_fixas(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "historico.db")
    db.inicializar()

    db.adicionar_ignorada("  Aelin ")
    db.adicionar_ignorada("aelin")  # repetida, não duplica
    db.adicionar_fixa("Tava", "estava")
    db.adicionar_fixa("tava", "estava mesmo")  # atualiza a existente
    assert db.listar_ignoradas() == ["aelin"]
    assert db.listar_fixas() == {"tava": "estava mesmo"}

    db.remover_ignorada("aelin")
    db.remover_fixa("tava")
    assert db.listar_ignoradas() == []
    assert db.listar_fixas() == {}
