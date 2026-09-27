import difflib
import html
import re

ESTILO = """
<style>
.diferencas { white-space: pre-wrap; line-height: 1.7; font-size: 0.95rem; }
.diferencas del { background: rgba(255, 75, 75, 0.22); text-decoration: line-through; }
.diferencas ins { background: rgba(33, 195, 84, 0.25); text-decoration: none; }
</style>
"""


def _tokens(texto: str) -> list[str]:
    # Palavras, espaços e pontuação separados: a diferença mostra só o que mudou.
    return re.findall(r"\w+|\s+|[^\w\s]", texto)


def destacar(original: str, novo: str) -> str:
    """HTML do texto novo com o que saiu riscado e o que entrou destacado."""
    a, b = _tokens(original), _tokens(novo)
    partes = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            partes.append(html.escape("".join(a[i1:i2])))
            continue
        if i2 > i1:
            partes.append(f"<del>{html.escape(''.join(a[i1:i2]))}</del>")
        if j2 > j1:
            partes.append(f"<ins>{html.escape(''.join(b[j1:j2]))}</ins>")
    return f'{ESTILO}<div class="diferencas">{"".join(partes)}</div>'
