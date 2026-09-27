import json
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path

from corretor import MOTIVO_FIXA

DB_PATH = Path(__file__).parent / "historico.db"
VERSAO_BACKUP = 1


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
                observacoes     TEXT NOT NULL DEFAULT '',
                arquivo         TEXT NOT NULL DEFAULT ''
            )
            """
        )
        # Bancos de versões anteriores não têm as colunas mais novas.
        colunas = {linha["name"] for linha in conn.execute("PRAGMA table_info(historico)")}
        novas = {
            "arquivo": "TEXT NOT NULL DEFAULT ''",
            # Edição manual do texto corrigido; vazio quando não houve.
            "texto_final": "TEXT NOT NULL DEFAULT ''",
            # O .docx enviado, para devolver as correções com a formatação original.
            "arquivo_dados": "BLOB",
        }
        for coluna, tipo in novas.items():
            if coluna not in colunas:
                conn.execute(f"ALTER TABLE historico ADD COLUMN {coluna} {tipo}")
        # Dicionário pessoal: guardado em minúsculas, a comparação ignora maiúsculas.
        conn.execute("CREATE TABLE IF NOT EXISTS palavras_ignoradas (palavra TEXT PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS correcoes_fixas (original TEXT PRIMARY KEY, corrigido TEXT NOT NULL)")
        # Revisões da IA por parágrafo: um texto longo interrompido continua de onde parou.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cache_ia (modelo TEXT NOT NULL, paragrafo TEXT NOT NULL,"
            " revisado TEXT NOT NULL, PRIMARY KEY (modelo, paragrafo))"
        )
        # Avisos silenciados: id da regra e um exemplo da mensagem, para o autor reconhecer.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS regras_desligadas (regra TEXT PRIMARY KEY, descricao TEXT NOT NULL DEFAULT '')"
        )


def salvar(
    texto_original: str,
    texto_corrigido: str,
    correcoes: list[dict],
    observacoes: list[dict],
    arquivo: str = "",
    arquivo_dados: bytes | None = None,
) -> int:
    with closing(_conectar()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO historico (texto_original, texto_corrigido, correcoes, observacoes, arquivo, arquivo_dados)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                texto_original,
                texto_corrigido,
                json.dumps(correcoes, ensure_ascii=False),
                json.dumps(observacoes, ensure_ascii=False),
                arquivo,
                arquivo_dados,
            ),
        )
        return cur.lastrowid


def _observacoes(valor: str) -> list[dict]:
    if valor.startswith("["):
        return json.loads(valor)
    # Versões anteriores guardavam as observações como texto pronto, uma por linha.
    return [
        {"trecho": "", "mensagem": linha.removeprefix("- "), "sugestao": None, "regra": "", "tipo": "estilo"}
        for linha in valor.splitlines()
        if linha.strip()
    ]


def _para_dict(linha: sqlite3.Row) -> dict:
    correcoes = json.loads(linha["correcoes"])
    # Registros da versão anterior (API da Anthropic) não tinham tipo nem aceite.
    for c in correcoes:
        c.setdefault("tipo", "automatica")
        c.setdefault("aceita", True)
    registro = {**dict(linha), "correcoes": correcoes, "observacoes": _observacoes(linha["observacoes"])}
    registro.setdefault("texto_final", "")
    registro.setdefault("arquivo_dados", None)
    return registro


def _filtro(busca: str) -> tuple[str, tuple]:
    if not busca.strip():
        return "", ()
    termo = f"%{busca.strip()}%"
    return " WHERE arquivo LIKE ? OR texto_original LIKE ? OR data LIKE ?", (termo, termo, termo)


def listar(busca: str = "", limite: int | None = None, deslocamento: int = 0) -> list[dict]:
    where, parametros = _filtro(busca)
    sql = f"SELECT * FROM historico{where} ORDER BY id DESC"
    if limite is not None:
        sql += " LIMIT ? OFFSET ?"
        parametros += (limite, deslocamento)
    with closing(_conectar()) as conn:
        linhas = conn.execute(sql, parametros).fetchall()
    return [_para_dict(l) for l in linhas]


def contar(busca: str = "") -> int:
    where, parametros = _filtro(busca)
    with closing(_conectar()) as conn:
        return conn.execute(f"SELECT COUNT(*) FROM historico{where}", parametros).fetchone()[0]


def excluir(registro_id: int) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute("DELETE FROM historico WHERE id = ?", (registro_id,))


def obter(registro_id: int) -> dict | None:
    with closing(_conectar()) as conn:
        linha = conn.execute("SELECT * FROM historico WHERE id = ?", (registro_id,)).fetchone()
    return _para_dict(linha) if linha else None


def atualizar(
    registro_id: int, texto_corrigido: str, correcoes: list[dict], observacoes: list[dict] | None = None
) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute(
            "UPDATE historico SET texto_corrigido = ?, correcoes = ? WHERE id = ?",
            (texto_corrigido, json.dumps(correcoes, ensure_ascii=False), registro_id),
        )
        if observacoes is not None:
            conn.execute(
                "UPDATE historico SET observacoes = ? WHERE id = ?",
                (json.dumps(observacoes, ensure_ascii=False), registro_id),
            )


def salvar_edicao(registro_id: int, texto_final: str) -> None:
    """Guarda a edição manual do texto corrigido; texto vazio descarta a edição."""
    with closing(_conectar()) as conn, conn:
        conn.execute("UPDATE historico SET texto_final = ? WHERE id = ?", (texto_final, registro_id))


def listar_ignoradas() -> list[str]:
    with closing(_conectar()) as conn:
        return [l["palavra"] for l in conn.execute("SELECT palavra FROM palavras_ignoradas ORDER BY palavra")]


def adicionar_ignorada(palavra: str) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute("INSERT OR IGNORE INTO palavras_ignoradas (palavra) VALUES (?)", (palavra.strip().lower(),))


def remover_ignorada(palavra: str) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute("DELETE FROM palavras_ignoradas WHERE palavra = ?", (palavra,))


def listar_fixas() -> dict[str, str]:
    with closing(_conectar()) as conn:
        linhas = conn.execute("SELECT original, corrigido FROM correcoes_fixas ORDER BY original")
        return {l["original"]: l["corrigido"] for l in linhas}


def adicionar_fixa(original: str, corrigido: str) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute(
            "INSERT OR REPLACE INTO correcoes_fixas (original, corrigido) VALUES (?, ?)",
            (original.strip().lower(), corrigido.strip()),
        )


def remover_fixa(original: str) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute("DELETE FROM correcoes_fixas WHERE original = ?", (original,))


def listar_regras() -> dict[str, str]:
    with closing(_conectar()) as conn:
        linhas = conn.execute("SELECT regra, descricao FROM regras_desligadas ORDER BY regra")
        return {l["regra"]: l["descricao"] for l in linhas}


def adicionar_regra(regra: str, descricao: str = "") -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute("INSERT OR REPLACE INTO regras_desligadas (regra, descricao) VALUES (?, ?)", (regra, descricao))


def remover_regra(regra: str) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute("DELETE FROM regras_desligadas WHERE regra = ?", (regra,))


def sugestoes_de_fixas(minimo: int = 3) -> list[tuple[str, str, int]]:
    """Correções de palavra aceitas várias vezes no histórico: candidatas a correção fixa.

    Retorna (original, corrigido, vezes), da mais frequente para a menos. Ficam de fora
    as que já são fixas e as palavras aceitas do dicionário.
    """
    with closing(_conectar()) as conn:
        linhas = conn.execute("SELECT correcoes FROM historico").fetchall()
    ja_tratadas = set(listar_fixas()) | set(listar_ignoradas())
    contagem = Counter()
    for linha in linhas:
        for c in json.loads(linha["correcoes"]):
            original = c.get("original", "")
            if (
                c.get("aceita", True)
                and c.get("motivo") != MOTIVO_FIXA
                and original.isalpha()
                and original.lower() not in ja_tratadas
            ):
                contagem[(original.lower(), c["corrigido"].lower())] += 1
    return [(o, c, n) for (o, c), n in contagem.most_common() if n >= minimo]


def ler_revisao_ia(modelo: str, paragrafo: str) -> str | None:
    with closing(_conectar()) as conn:
        linha = conn.execute(
            "SELECT revisado FROM cache_ia WHERE modelo = ? AND paragrafo = ?", (modelo, paragrafo)
        ).fetchone()
    return linha["revisado"] if linha else None


def gravar_revisao_ia(modelo: str, paragrafo: str, revisado: str) -> None:
    with closing(_conectar()) as conn, conn:
        conn.execute(
            "INSERT OR REPLACE INTO cache_ia (modelo, paragrafo, revisado) VALUES (?, ?, ?)",
            (modelo, paragrafo, revisado),
        )


def exportar() -> dict:
    """Dicionário pessoal e histórico (sem os arquivos .docx) para backup."""
    with closing(_conectar()) as conn:
        linhas = conn.execute(
            "SELECT data, texto_original, texto_corrigido, correcoes, observacoes, arquivo, texto_final"
            " FROM historico ORDER BY id"
        ).fetchall()
    historico = [
        {**dict(l), "correcoes": json.loads(l["correcoes"]), "observacoes": _observacoes(l["observacoes"])}
        for l in linhas
    ]
    return {
        "versao": VERSAO_BACKUP,
        "palavras_aceitas": listar_ignoradas(),
        "correcoes_fixas": listar_fixas(),
        "regras_desligadas": listar_regras(),
        "historico": historico,
    }


def importar(dados: dict) -> dict[str, int]:
    """Junta um backup ao que já existe. Registros do histórico já presentes não são duplicados."""
    if not isinstance(dados, dict) or dados.get("versao") != VERSAO_BACKUP:
        raise ValueError("Arquivo de backup inválido ou de outra versão.")
    for palavra in dados.get("palavras_aceitas", []):
        adicionar_ignorada(palavra)
    for original, corrigido in dados.get("correcoes_fixas", {}).items():
        adicionar_fixa(original, corrigido)
    for regra, descricao in dados.get("regras_desligadas", {}).items():
        adicionar_regra(regra, descricao)

    novos = 0
    with closing(_conectar()) as conn, conn:
        for r in dados.get("historico", []):
            existe = conn.execute(
                "SELECT 1 FROM historico WHERE data = ? AND texto_original = ?", (r["data"], r["texto_original"])
            ).fetchone()
            if existe:
                continue
            conn.execute(
                "INSERT INTO historico (data, texto_original, texto_corrigido, correcoes, observacoes, arquivo,"
                " texto_final) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    r["data"],
                    r["texto_original"],
                    r["texto_corrigido"],
                    json.dumps(r["correcoes"], ensure_ascii=False),
                    json.dumps(r.get("observacoes", []), ensure_ascii=False),
                    r.get("arquivo", ""),
                    r.get("texto_final", ""),
                ),
            )
            novos += 1
    return {
        "palavras_aceitas": len(dados.get("palavras_aceitas", [])),
        "correcoes_fixas": len(dados.get("correcoes_fixas", {})),
        "regras_desligadas": len(dados.get("regras_desligadas", {})),
        "historico": novos,
    }
