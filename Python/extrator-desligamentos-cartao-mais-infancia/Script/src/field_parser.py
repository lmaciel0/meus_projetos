"""
Módulo de interpretação de campos.
Extrai campos específicos do texto do PDF: MUNICIPIO, CPF, NIS, NOME, MOTIVO.
"""

import re
import logging
from typing import Dict, Optional
from unicodedata import normalize


logger = logging.getLogger(__name__)


class FieldParser:
    """Parser para extrair campos do texto de desligamento."""
    
    def parse(self, texto: str) -> Dict[str, str]:
        """
        Extrai todos os campos do texto.
        
        Args:
            texto: Texto extraído do PDF
            
        Returns:
            Dicionário com os campos: MUNICIPIO, CPF, NIS, NOME, MOTIVO
        """
        
        return {
            'MUNICIPIO': self._extract_municipio(texto),
            'CPF': self._extract_cpf(texto),
            'NIS': self._extract_nis(texto),
            'NOME': self._extract_nome(texto),
            'MOTIVO': self._extract_motivo(texto),
        }
    
    @staticmethod
    def _normalize(text: str) -> str:
        """Normaliza espaços e quebras de linha."""
        # Remove espaços extras e quebras de linha
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def _remove_accents(text: str) -> str:
        """Remove acentos para facilitar busca."""
        return normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    
    def _extract_municipio(self, texto: str) -> str:
        """Extrai MUNICIPIO após 'MUNICÍPIO:'."""
        
        # Buscar padrão: MUNICÍPIO: <valor>
        padrao = r'MUNICÍPIO\s*:\s*([^\n]+)'
        match = re.search(padrao, texto, re.IGNORECASE)
        
        if match:
            valor = self._normalize(match.group(1))
            # Limpar valor (remover números após o nome da cidade, etc)
            valor = re.sub(r'\s*\d+\s*$', '', valor)
            return valor
        
        return ""
    
    def _extract_cpf(self, texto: str) -> str:
        """
        Extrai CPF mantendo 11 dígitos como texto.
        Preserva zeros à esquerda.
        """
        
        # Buscar padrão: CPF: <valor>
        padrao = r'CPF\s*:\s*([^\n]+)'
        match = re.search(padrao, texto, re.IGNORECASE)
        
        if match:
            valor = match.group(1).strip()
            
            # Extrair apenas dígitos
            digitos = re.sub(r'\D', '', valor)
            
            # Retornar os 11 primeiros dígitos como texto (preservando zeros à esquerda)
            if len(digitos) >= 11:
                return digitos[:11]
            elif len(digitos) > 0:
                # Se houver menos de 11 dígitos, retornar o que temos
                logger.warning(f"CPF com menos de 11 dígitos encontrado: {digitos}")
                return digitos
        
        return ""
    
    def _extract_nis(self, texto: str) -> str:
        """
        Extrai NIS mantendo todos os dígitos como texto.
        Preserva zeros à esquerda.
        """
        
        # Buscar padrão: NIS: <valor>
        padrao = r'NIS\s*:\s*([^\n]+)'
        match = re.search(padrao, texto, re.IGNORECASE)
        
        if match:
            valor = match.group(1).strip()
            
            # Extrair apenas dígitos
            digitos = re.sub(r'\D', '', valor)
            
            return digitos if digitos else ""
        
        return ""
    
    def _extract_nome(self, texto: str) -> str:
        """
        Extrai NOME após 'NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO:'.
        """
        
        # Buscar padrão: NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: <valor>
        padrao = r'NOME\s+DO\s+RESPONSÁVEL\s+FAMILIAR\s*\(RF\)\s+A\s+SER\s+DESLIGADO\s*:\s*([^\n]+)'
        match = re.search(padrao, texto, re.IGNORECASE)
        
        if match:
            valor = self._normalize(match.group(1))
            # Remover números e caracteres especiais no final
            valor = re.sub(r'[\d\(\)\-]+\s*$', '', valor)
            return valor.strip()
        
        return ""
    
    def _extract_motivo(self, texto: str) -> str:
        """
        Extrai MOTIVO identificando qual alternativa tem 'X' dentro de parênteses
        na seção 'MOTIVO DO DESLIGAMENTO'.
        """
        
        # Encontrar a seção de motivo
        padrao_secao = r'MOTIVO\s+DO\s+DESLIGAMENTO(.*?)(?=\n\n|$)'
        match_secao = re.search(padrao_secao, texto, re.IGNORECASE | re.DOTALL)
        
        if not match_secao:
            return ""
        
        secao = match_secao.group(1)
        
        # Procurar por padrões como ( X ) ou (X)
        # Cada linha pode ser uma opção, procuramos aquela com X marcado
        
        linhas = secao.split('\n')
        motivos = []
        
        for i, linha in enumerate(linhas):
            # Procurar por (X) ou ( X ) ou (x)
            if re.search(r'\(\s*[xX]\s*\)', linha):
                # Encontrou uma opção marcada
                # Limpar a linha para extrair o texto
                motivo = re.sub(r'\(\s*[xX]\s*\)\s*', '', linha)
                motivo = self._normalize(motivo)
                
                if motivo:
                    motivos.append(motivo)
                    
                    # Se for "OUTRO", procurar pela descrição na próxima linha
                    if re.search(r'OUTRO', motivo, re.IGNORECASE):
                        if i + 1 < len(linhas):
                            descricao = self._normalize(linhas[i + 1])
                            if descricao and not re.search(r'\(\s*[xX]\s*\)', descricao):
                                motivo = f"{motivo}: {descricao}"
                                motivos[-1] = motivo
        
        # Retornar o motivo encontrado (geralmente só um)
        if motivos:
            return motivos[0]
        
        return ""
