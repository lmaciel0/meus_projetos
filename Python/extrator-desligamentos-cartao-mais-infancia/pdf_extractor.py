"""Extração de texto nativo e fallback de OCR para PDFs."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    pytesseract = None
    convert_from_path = None


class PDFExtractor:
    def __init__(self, ocr_enabled: bool = True):
        self.ocr_enabled = ocr_enabled

    def extract(self, pdf_path: str | Path) -> str:
        path = Path(pdf_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        text = self._pdfplumber(path)
        if text.strip() or not self.ocr_enabled:
            return text
        return self._ocr(path)

    @staticmethod
    def _pdfplumber(path: Path) -> str:
        if pdfplumber is None:
            return ""
        try:
            with pdfplumber.open(path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            logger.exception("Falha na extração nativa de %s", path.name)
            return ""

    @staticmethod
    def _ocr(path: Path) -> str:
        if pytesseract is None or convert_from_path is None:
            return ""
        try:
            pages = convert_from_path(str(path))
            return "\n".join(pytesseract.image_to_string(page, lang="por") for page in pages)
        except Exception:
            logger.exception("Falha no OCR de %s", path.name)
            return ""