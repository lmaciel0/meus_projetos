import json
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).parent / "historico.db"


def _conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar() -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS historico (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                data            TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                texto_original  TEXT NOT NULL,
                texto_corrigido TEXT NOT NULL,
                correcoes       TEXT NOT NULL,
                observacoes     TEXT NOT NULL DEFAULT ''
            )
            """
        )


def salvar(texto_original: str, texto_corrigido: str, correcoes: list[dict], observacoes: str) -> int:
    with closing(_conectar()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO historico (texto_original, texto_corrigido, correcoes, observacoes) VALUES (?, ?, ?, ?)",
            (texto_original, texto_corrigido, json.dumps(correcoes, ensure_ascii=False), observacoes),
        )
        return cur.lastrowid


def _para_dict(linha: sqlite3.Row) -> dict:
    correcoes = json.loads(linha["correcoes"])
    # Registros da versão anterior (API da Anthropic) não tinham tipo nem aceite.
    for c in correcoes:
        c.setdefault("tipo", "automatica")
        c.setdefault("aceita", True)
    return {**dict(linha), "correcoes": correcoes}


def listar() -> list[dict]:
    with closing(_conectar()) as conn:
        linhas = conn.execute("SELECT * FROM historico ORDER BY id DESC").fetchall()
    return [_para_dict(l) for l in linhas]


def excluir(registro_id: int) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute("DELETE FROM historico WHERE id = ?", (registro_id,))


def obter(registro_id: int) -> dict | None:
    with closing(_conectar()) as conn:
        linha = conn.execute("SELECT * FROM historico WHERE id = ?", (registro_id,)).fetchone()
    return _para_dict(linha) if linha else None


def atualizar(registro_id: int, texto_corrigido: str, correcoes: list[dict]) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute(
            "UPDATE historico SET texto_corrigido = ?, correcoes = ? WHERE id = ?",
            (texto_corrigido, json.dumps(correcoes, ensure_ascii=False), registro_id),
        )
