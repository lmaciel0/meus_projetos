"""
Script auxiliar para facilitar o uso do Leitor de Desligamentos.
Fornece função para integração em outros scripts Python.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging

from main import DesligamentoProcessor


def processar_desligamentos(
    pasta_entrada: str,
    pasta_saida: str,
    formato: str = 'ambos',
    verboso: bool = False
) -> Dict:
    """
    Processa PDFs de desligamento programaticamente.
    
    Args:
        pasta_entrada: Caminho da pasta com PDFs
        pasta_saida: Caminho da pasta para salvar resultados
        formato: 'ambos', 'xlsx' ou 'csv'
        verboso: Ativar output detalhado
        
    Returns:
        Dicionário com estatísticas de processamento
        
    Exemplo:
        >>> stats = processar_desligamentos('./pdfs', './resultado')
        >>> print(f"Sucesso: {stats['sucesso']}, Revisar: {stats['revisar']}")
    """
    
    if verboso:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    processor = DesligamentoProcessor(pasta_entrada, pasta_saida)
    stats = processor.process()
    
    if stats['dados']:
        processor.export(stats, [formato])
    
    processor.print_summary(stats)
    
    return stats


def obter_dados_apenas(pasta_entrada: str, verboso: bool = False) -> List[Dict]:
    """
    Obtém dados extraídos sem exportar para arquivo.
    
    Args:
        pasta_entrada: Caminho da pasta com PDFs
        verboso: Ativar output detalhado
        
    Returns:
        Lista de dicionários com dados extraídos
        
    Exemplo:
        >>> dados = obter_dados_apenas('./pdfs')
        >>> for registro in dados:
        ...     print(f"{registro['NOME']} - {registro['MUNICIPIO']}")
    """
    
    if verboso:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    processor = DesligamentoProcessor(pasta_entrada, Path(pasta_entrada) / 'temp')
    stats = processor.process()
    
    return stats['dados']


if __name__ == '__main__':
    # Exemplo de uso
    print("Exemplo de uso do Leitor de Desligamentos")
    print("=" * 50)
    
    # Uso simples
    exemplo_pasta = Path.cwd() / 'pdfs'
    exemplo_saida = Path.cwd() / 'resultado'
    
    if exemplo_pasta.exists():
        print(f"Processando PDFs de {exemplo_pasta}...")
        stats = processar_desligamentos(
            str(exemplo_pasta),
            str(exemplo_saida),
            formato='ambos',
            verboso=True
        )
    else:
        print(f"Pasta de exemplo não encontrada: {exemplo_pasta}")
        print("Crie uma pasta 'pdfs' com seus arquivos PDF para testar.")
