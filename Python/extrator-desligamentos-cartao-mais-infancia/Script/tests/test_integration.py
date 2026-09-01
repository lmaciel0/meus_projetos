"""
Testes de integração para o Leitor de Desligamentos CMIC.
Testa o fluxo completo de processamento.
"""

import unittest
import tempfile
from pathlib import Path
import json
import sys

# Adicionar diretórios ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import DesligamentoProcessor
from export_handler import ExportHandler
from pdf_extraction import PDFExtractor
from field_parser import FieldParser
from test_data import EXEMPLO_PDF_TEXTO, DADOS_ESPERADOS_1


class TestFluxoCompleto(unittest.TestCase):
    """Testa o fluxo completo de processamento."""
    
    def setUp(self):
        """Configurar para cada teste."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.entrada = Path(self.temp_dir.name) / 'entrada'
        self.saida = Path(self.temp_dir.name) / 'saida'
        self.entrada.mkdir()
        self.saida.mkdir()
    
    def tearDown(self):
        """Limpar após cada teste."""
        self.temp_dir.cleanup()
    
    def test_processor_init(self):
        """Testa inicialização do processador."""
        processor = DesligamentoProcessor(str(self.entrada), str(self.saida))
        
        self.assertIsNotNone(processor)
        self.assertEqual(processor.input_dir, self.entrada)
        self.assertEqual(processor.output_dir, self.saida)
    
    def test_process_pasta_vazia(self):
        """Testa processamento de pasta vazia."""
        processor = DesligamentoProcessor(str(self.entrada), str(self.saida))
        stats = processor.process()
        
        self.assertEqual(stats['total_processados'], 0)
        self.assertEqual(stats['sucesso'], 0)
        self.assertEqual(stats['revisar'], 0)
    
    def test_field_parser_com_dados_reais(self):
        """Testa parser com dados simulados reais."""
        parser = FieldParser()
        resultado = parser.parse(EXEMPLO_PDF_TEXTO)
        
        self.assertEqual(resultado['MUNICIPIO'], 'FORTALEZA')
        self.assertEqual(resultado['CPF'], '12345678900')
        self.assertEqual(resultado['NIS'], '12345678900')
        self.assertEqual(resultado['NOME'], 'JOÃO SILVA SANTOS')
        self.assertIn('Mudança para outro Estado', resultado['MOTIVO'])
    
    def test_export_handler_xlsx(self):
        """Testa exportação para XLSX."""
        exportador = ExportHandler()
        dados = [DADOS_ESPERADOS_1]
        
        xlsx_path = str(self.saida / 'teste.xlsx')
        
        try:
            exportador.export_xlsx(dados, xlsx_path)
            self.assertTrue(Path(xlsx_path).exists())
        except ImportError:
            self.skipTest("pandas/openpyxl não disponível")
    
    def test_export_handler_csv(self):
        """Testa exportação para CSV."""
        exportador = ExportHandler()
        dados = [DADOS_ESPERADOS_1]
        
        csv_path = str(self.saida / 'teste.csv')
        
        try:
            exportador.export_csv(dados, csv_path)
            self.assertTrue(Path(csv_path).exists())
            
            # Verificar conteúdo
            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('MUNICIPIO', content)
                self.assertIn('FORTALEZA', content)
        except ImportError:
            self.skipTest("pandas não disponível")


class TestValidacaoDados(unittest.TestCase):
    """Testa validação de dados extraídos."""
    
    def test_cpf_preserva_zeros(self):
        """Testa que CPF preserva zeros à esquerda."""
        parser = FieldParser()
        
        texto = "CPF: 001.234.567-89"
        resultado = parser._extract_cpf(texto)
        
        self.assertEqual(resultado, "00123456789")
        self.assertTrue(resultado.startswith("00"))
    
    def test_nis_preserva_zeros(self):
        """Testa que NIS preserva zeros à esquerda."""
        parser = FieldParser()
        
        texto = "NIS: 001.234.567-89"
        resultado = parser._extract_nis(texto)
        
        self.assertEqual(resultado, "00123456789")
        self.assertTrue(resultado.startswith("00"))
    
    def test_campos_obrigatorios_vazios(self):
        """Testa que campos vazios são tratados."""
        parser = FieldParser()
        
        texto = "Texto sem nenhum campo obrigatório"
        resultado = parser.parse(texto)
        
        for campo in ['MUNICIPIO', 'CPF', 'NIS', 'NOME', 'MOTIVO']:
            self.assertEqual(resultado[campo], "")


if __name__ == '__main__':
    unittest.main()
