"""
Módulo de extração de texto de PDFs.
Suporta extração nativa com pdfplumber e OCR com pytesseract como fallback.
"""

import logging
from pathlib import Path
from typing import Optional
import re

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


logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extrai texto de arquivos PDF usando pdfplumber e OCR como fallback."""
    
    def __init__(self, ocr_enabled: bool = True):
        """
        Inicializa o extrator.
        
        Args:
            ocr_enabled: Habilita OCR como fallback (padrão: True)
        """
        self.ocr_enabled = ocr_enabled
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extrai texto de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Texto extraído do PDF
        """
        
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
        
        # Tentar extração nativa com pdfplumber
        if pdfplumber:
            texto = self._extract_with_pdfplumber(str(pdf_path))
            if texto.strip():
                logger.debug(f"Extração bem-sucedida com pdfplumber: {pdf_path.name}")
                return texto
            else:
                logger.debug(f"pdfplumber retornou texto vazio para {pdf_path.name}")
        
        # Fallback para OCR
        if self.ocr_enabled and pytesseract and convert_from_path:
            logger.info(f"Usando OCR para {pdf_path.name}")
            texto = self._extract_with_ocr(str(pdf_path))
            if texto.strip():
                return texto
            else:
                logger.warning(f"OCR também retornou texto vazio para {pdf_path.name}")
        
        return ""
    
    @staticmethod
    def _extract_with_pdfplumber(pdf_path: str) -> str:
        """Extrai texto usando pdfplumber."""
        
        try:
            textos = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    texto = page.extract_text()
                    if texto:
                        textos.append(texto)
            
            return "\n".join(textos)
        
        except Exception as e:
            logger.error(f"Erro ao extrair com pdfplumber: {str(e)}")
            return ""
    
    @staticmethod
    def _extract_with_ocr(pdf_path: str) -> str:
        """Extrai texto usando OCR (pytesseract + pdf2image)."""
        
        try:
            # Converter PDF para imagens
            images = convert_from_path(pdf_path)
            textos = []
            
            for page_num, image in enumerate(images, 1):
                try:
                    # Extrair texto da imagem
                    texto = pytesseract.image_to_string(
                        image,
                        lang='por'  # Português
                    )
                    if texto:
                        textos.append(texto)
                except Exception as e:
                    logger.warning(f"Erro ao processar página {page_num} com OCR: {str(e)}")
            
            return "\n".join(textos)
        
        except Exception as e:
            logger.error(f"Erro ao extrair com OCR: {str(e)}")
            return ""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normaliza o texto extraído.
        Remove linhas em branco extras, normaliza espaços.
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text)
        
        # Remover espaços antes de pontuação
        text = re.sub(r'\s+([.,;:])', r'\1', text)
        
        return text.strip()
