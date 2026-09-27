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
    novo = db.salvar("b", "b", [], [], arquivo="conto.pdf")

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


def _banco(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "historico.db")
    db.inicializar()


def test_observacoes_antigas_em_texto_viram_lista(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    rid = db.salvar("a", "a", [], [])
    with sqlite3.connect(db.DB_PATH) as conn:
        conn.execute("UPDATE historico SET observacoes = ? WHERE id = ?", ("- “ai”: Coloquial.\n- Outra.", rid))
    conn.close()
    observacoes = db.obter(rid)["observacoes"]
    assert [o["mensagem"] for o in observacoes] == ["“ai”: Coloquial.", "Outra."]


def test_edicao_manual_e_observacoes_sao_salvas(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    rid = db.salvar("a", "b", [], [{"trecho": "x", "mensagem": "m"}], arquivo="c.docx", arquivo_dados=b"PK")
    db.salvar_edicao(rid, "editado")
    db.atualizar(rid, "b", [], [{"trecho": "x", "mensagem": "m", "dispensada": True}])
    r = db.obter(rid)
    assert (r["texto_final"], r["arquivo_dados"], r["observacoes"][0]["dispensada"]) == ("editado", b"PK", True)


def test_busca_e_paginacao(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    for i in range(5):
        db.salvar(f"texto {i}", "", [], [], arquivo="capitulo.docx" if i % 2 else "")
    assert db.contar() == 5
    assert db.contar("capitulo") == 2
    assert [r["texto_original"] for r in db.listar(limite=2, deslocamento=1)] == ["texto 3", "texto 2"]
    assert [r["texto_original"] for r in db.listar("texto 4")] == ["texto 4"]


def test_regras_desligadas(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    db.adicionar_regra("REPETICAO_PROXIMA", "Repetida.")
    assert db.listar_regras() == {"REPETICAO_PROXIMA": "Repetida."}
    db.remover_regra("REPETICAO_PROXIMA")
    assert db.listar_regras() == {}


def test_sugere_correcao_fixa_aceita_varias_vezes(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    tava = {"original": "Tava", "corrigido": "Estava", "aceita": True, "tipo": "automatica", "motivo": "x"}
    recusada = {**tava, "original": "ta", "corrigido": "tá", "aceita": False}
    for _ in range(3):
        db.salvar("t", "t", [tava, recusada], [])
    assert db.sugestoes_de_fixas() == [("tava", "estava", 3)]
    db.adicionar_fixa("tava", "estava")
    assert db.sugestoes_de_fixas() == []


def test_backup_exporta_e_importa_sem_duplicar(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    db.adicionar_ignorada("Aelin")
    db.adicionar_fixa("tava", "estava")
    db.adicionar_regra("R", "d")
    db.salvar("original", "corrigido", [], [], arquivo_dados=b"PK")
    backup = db.exportar()
    assert "arquivo_dados" not in backup["historico"][0]

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "outro.db")
    db.inicializar()
    assert db.importar(backup)["historico"] == 1
    assert db.importar(backup)["historico"] == 0  # já existe
    assert db.listar_ignoradas() == ["aelin"] and db.listar_fixas() == {"tava": "estava"}
    assert db.listar_regras() == {"R": "d"} and db.contar() == 1


def test_backup_invalido(tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch)
    import pytest

    with pytest.raises(ValueError):
        db.importar({"versao": 99})
