import importlib.util
import io
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

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


def _comando_ocr() -> list[str] | None:
    """OCRmyPDF, se estiver instalado (ele também precisa do Tesseract com o idioma português)."""
    if executavel := shutil.which("ocrmypdf"):
        return [executavel]
    if importlib.util.find_spec("ocrmypdf"):
        return [sys.executable, "-m", "ocrmypdf"]
    return None


def _ocr(dados: bytes) -> bytes | None:
    """Reconhece o texto de um PDF escaneado. Retorna None se não houver OCR instalado."""
    comando = _comando_ocr()
    if comando is None:
        return None
    with tempfile.TemporaryDirectory() as pasta:
        entrada, saida = Path(pasta) / "entrada.pdf", Path(pasta) / "saida.pdf"
        entrada.write_bytes(dados)
        try:
            subprocess.run(
                [*comando, "-l", "por", "--skip-text", "--output-type", "pdf", str(entrada), str(saida)],
                check=True,
                capture_output=True,
                timeout=900,
            )
        except subprocess.CalledProcessError as e:
            detalhe = e.stderr.decode(errors="replace").strip().splitlines()[-1:] or [""]
            raise ErroCorrecao(f"O OCR não conseguiu ler o PDF: {detalhe[0]}") from e
        except (subprocess.TimeoutExpired, OSError) as e:
            raise ErroCorrecao(f"O OCR não conseguiu ler o PDF: {e}") from e
        return saida.read_bytes()


def _ler(dados: bytes) -> str:
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
    return normalizar(texto)


def extrair_texto(dados: bytes) -> str:
    texto = _ler(dados)
    if texto:
        return texto
    # Sem texto: provavelmente escaneado. Tenta o OCR, se houver.
    reconhecido = _ocr(dados)
    if reconhecido is None:
        raise ErroCorrecao(
            "Não foi encontrado texto no PDF. Se ele for escaneado (imagem), instale o OCRmyPDF e o"
            " Tesseract com português para lê-lo aqui, ou passe-o por OCR antes."
        )
    texto = _ler(reconhecido)
    if not texto:
        raise ErroCorrecao("Não foi encontrado texto no PDF, nem com OCR.")
    return texto
