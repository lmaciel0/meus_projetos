import io
import re

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from corretor import ErroCorrecao

TRAVESSOES = ("—", "–")


def normalizar(texto: str) -> str:
    """Refaz os parágrafos do texto extraído de um PDF, que vem quebrado linha a linha.

    Sem isso o LanguageTool acusaria cada quebra de linha no meio da frase como erro.
    Parágrafo novo só em linha em branco ou em fala de diálogo (linha que começa com travessão).
    """
    paragrafos, atual = [], ""
    for linha in texto.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        linha = re.sub(r"\s+", " ", linha).strip()
        if linha.isdigit():  # número de página
            continue
        if not linha or linha.startswith(TRAVESSOES):
            if atual:
                paragrafos.append(atual)
            atual = linha
        elif not atual:
            atual = linha
        # "estra-\nda": só junta sem hífen quando a linha seguinte continua em minúscula.
        elif atual.endswith("-") and atual[-2:-1].isalpha() and linha[0].islower():
            atual = atual[:-1] + linha
        else:
            atual += " " + linha
    if atual:
        paragrafos.append(atual)
    return "\n\n".join(paragrafos)


def extrair_texto(dados: bytes) -> str:
    try:
        leitor = PdfReader(io.BytesIO(dados))
        if leitor.is_encrypted and not leitor.decrypt(""):
            raise ErroCorrecao("O PDF está protegido por senha. Remova a proteção e envie novamente.")
        # Páginas unidas por quebra simples: um parágrafo pode continuar na página seguinte.
        texto = "\n".join((pagina.extract_text() or "").rstrip() for pagina in leitor.pages)
    except ErroCorrecao:
        raise
    except (PdfReadError, ValueError, OSError) as e:
        raise ErroCorrecao(f"Não foi possível ler o PDF: {e}") from e

    texto = normalizar(texto)
    if not texto:
        raise ErroCorrecao(
            "Não foi encontrado texto no PDF. Se ele for escaneado (imagem), é preciso passá-lo por OCR antes."
        )
    return texto
