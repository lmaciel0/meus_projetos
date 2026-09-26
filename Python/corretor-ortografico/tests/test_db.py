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
