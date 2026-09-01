#!/usr/bin/env python3
"""
Leitor de Desligamentos - Cartão Mais Infância Ceará (CMIC)
Script principal para extrair dados de PDFs de desligamento e exportar para XLSX/CSV.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict
import logging

# Adicionar src ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pdf_extraction import PDFExtractor
from field_parser import FieldParser
from export_handler import ExportHandler


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DesligamentoProcessor:
    """Processa PDFs de desligamento e gera relatórios."""
    
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.pdf_extractor = PDFExtractor()
        self.field_parser = FieldParser()
        self.export_handler = ExportHandler()
        
    def process(self) -> Dict:
        """Processa todos os PDFs na pasta de entrada."""
        
        # Validar pasta de entrada
        if not self.input_dir.exists():
            logger.error(f"Pasta de entrada não existe: {self.input_dir}")
            sys.exit(1)
        
        # Criar pasta de saída
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Encontrar PDFs
        pdf_files = list(self.input_dir.glob('*.pdf')) + list(self.input_dir.glob('**/*.pdf'))
        
        if not pdf_files:
            logger.warning(f"Nenhum arquivo PDF encontrado em {self.input_dir}")
            return {
                'total': 0,
                'sucesso': 0,
                'revisar': 0,
                'erros': 0,
                'dados': []
            }
        
        logger.info(f"Encontrados {len(pdf_files)} arquivo(s) PDF")
        
        # Processar cada PDF
        resultados = []
        erros = []
        
        for pdf_file in sorted(pdf_files):
            try:
                logger.info(f"Processando: {pdf_file.name}")
                
                # Extrair texto do PDF
                texto = self.pdf_extractor.extract_text(str(pdf_file))
                
                if not texto:
                    logger.warning(f"Nenhum texto extraído de {pdf_file.name}")
                    erros.append({
                        'arquivo': pdf_file.name,
                        'erro': 'Nenhum texto extraído'
                    })
                    continue
                
                # Parse dos campos
                dados = self.field_parser.parse(texto)
                dados['ARQUIVO_ORIGEM'] = pdf_file.name
                
                # Determinar status de extração
                campos_obrigatorios = ['MUNICIPIO', 'CPF', 'NIS', 'NOME', 'MOTIVO']
                faltando = [c for c in campos_obrigatorios if not dados.get(c)]
                
                if faltando:
                    dados['STATUS_EXTRACAO'] = f"REVISAR - Campos faltando: {', '.join(faltando)}"
                else:
                    dados['STATUS_EXTRACAO'] = 'OK'
                
                resultados.append(dados)
                logger.info(f"✓ Extraído de {pdf_file.name}: {dados.get('NOME', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Erro ao processar {pdf_file.name}: {str(e)}")
                erros.append({
                    'arquivo': pdf_file.name,
                    'erro': str(e)
                })
        
        # Calcular estatísticas
        total = len(resultados)
        sucesso = sum(1 for r in resultados if r.get('STATUS_EXTRACAO') == 'OK')
        revisar = total - sucesso
        
        # Estatísticas de erro
        total_processados = total + len(erros)
        
        return {
            'total_processados': total_processados,
            'sucesso': sucesso,
            'revisar': revisar,
            'erros': len(erros),
            'dados': resultados,
            'erros_detalhes': erros
        }
    
    def export(self, stats: Dict, formatos: List[str]) -> None:
        """Exporta dados para os formatos solicitados."""
        
        if not stats['dados']:
            logger.warning("Nenhum dado para exportar")
            return
        
        timestamp = self._get_timestamp()
        
        # Exportar para XLSX
        if 'xlsx' in formatos or 'ambos' in formatos:
            xlsx_file = self.output_dir / f"desligamentos_{timestamp}.xlsx"
            self.export_handler.export_xlsx(stats['dados'], str(xlsx_file))
            logger.info(f"✓ Exportado para XLSX: {xlsx_file}")
        
        # Exportar para CSV
        if 'csv' in formatos or 'ambos' in formatos:
            csv_file = self.output_dir / f"desligamentos_{timestamp}.csv"
            self.export_handler.export_csv(stats['dados'], str(csv_file))
            logger.info(f"✓ Exportado para CSV: {csv_file}")
    
    def print_summary(self, stats: Dict) -> None:
        """Imprime resumo das operações."""
        
        print("\n" + "="*60)
        print("RESUMO DO PROCESSAMENTO")
        print("="*60)
        print(f"Total de arquivos processados: {stats['total_processados']}")
        print(f"Extrações bem-sucedidas:       {stats['sucesso']}")
        print(f"Extrações que exigem revisão:  {stats['revisar']}")
        print(f"Erros ao processar:            {stats['erros']}")
        print("="*60)
        
        if stats.get('erros_detalhes'):
            print("\nARQUIVOS COM ERRO:")
            for erro in stats['erros_detalhes']:
                print(f"  - {erro['arquivo']}: {erro['erro']}")
        
        print()
    
    @staticmethod
    def _get_timestamp() -> str:
        """Retorna timestamp formatado para nomes de arquivo."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")


def main():
    """Função principal."""
    
    parser = argparse.ArgumentParser(
        description='Extrator de dados de PDFs de Desligamento - CMIC',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos de uso:
  python main.py --entrada ./pdfs --saida ./resultado --formato ambos
  python main.py --entrada ./pdfs --saida ./resultado --formato xlsx
  python main.py --entrada ./pdfs --saida ./resultado --formato csv
        '''
    )
    
    parser.add_argument(
        '--entrada',
        required=True,
        help='Pasta contendo os PDFs de entrada'
    )
    
    parser.add_argument(
        '--saida',
        required=True,
        help='Pasta onde serão salvos os arquivos exportados'
    )
    
    parser.add_argument(
        '--formato',
        choices=['xlsx', 'csv', 'ambos'],
        default='ambos',
        help='Formato(s) de exportação (padrão: ambos)'
    )
    
    args = parser.parse_args()
    
    # Criar processador
    processor = DesligamentoProcessor(args.entrada, args.saida)
    
    # Processar PDFs
    logger.info(f"Iniciando processamento de PDFs em {args.entrada}")
    stats = processor.process()
    
    # Exportar resultados
    if stats['dados']:
        processor.export(stats, [args.formato])
    
    # Exibir resumo
    processor.print_summary(stats)


if __name__ == '__main__':
    main()
