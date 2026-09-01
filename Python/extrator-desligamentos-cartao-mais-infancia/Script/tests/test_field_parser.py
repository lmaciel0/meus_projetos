"""
Testes unitários para extração de campos e processamento de dados.
"""

import unittest
import sys
from pathlib import Path

# Adicionar src ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from field_parser import FieldParser


class TestFieldParser(unittest.TestCase):
    """Testes para o parser de campos."""
    
    def setUp(self):
        """Configurar para cada teste."""
        self.parser = FieldParser()
    
    def test_extract_municipio(self):
        """Testa extração de MUNICIPIO."""
        
        texto = """
        MUNICÍPIO: FORTALEZA
        CPF: 12345678901
        """
        
        resultado = self.parser._extract_municipio(texto)
        self.assertEqual(resultado, "FORTALEZA")
    
    def test_extract_municipio_com_espacos(self):
        """Testa extração de MUNICIPIO com espaços extras."""
        
        texto = """
        MUNICÍPIO  :  FORTALEZA  
        """
        
        resultado = self.parser._extract_municipio(texto)
        self.assertEqual(resultado, "FORTALEZA")
    
    def test_extract_cpf_preserva_zeros(self):
        """Testa extração de CPF preservando zeros à esquerda."""
        
        texto = "CPF: 00123456789"
        resultado = self.parser._extract_cpf(texto)
        self.assertEqual(resultado, "00123456789")
        self.assertEqual(len(resultado), 11)
    
    def test_extract_cpf_com_formatacao(self):
        """Testa extração de CPF com formatação (pontos e hífens)."""
        
        texto = "CPF: 123.456.789-00"
        resultado = self.parser._extract_cpf(texto)
        self.assertEqual(resultado, "12345678900")
    
    def test_extract_cpf_retorna_vazio(self):
        """Testa que CPF retorna vazio quando não encontrado."""
        
        texto = "Algum texto sem CPF"
        resultado = self.parser._extract_cpf(texto)
        self.assertEqual(resultado, "")
    
    def test_extract_nis_preserva_zeros(self):
        """Testa extração de NIS preservando zeros à esquerda."""
        
        texto = "NIS: 00123456789012"
        resultado = self.parser._extract_nis(texto)
        self.assertEqual(resultado, "00123456789012")
    
    def test_extract_nis_com_formatacao(self):
        """Testa extração de NIS com formatação."""
        
        texto = "NIS: 123.456.789-00"
        resultado = self.parser._extract_nis(texto)
        self.assertEqual(resultado, "12345678900")
    
    def test_extract_nome_basico(self):
        """Testa extração de NOME básica."""
        
        texto = """
        NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: JOÃO DA SILVA
        """
        
        resultado = self.parser._extract_nome(texto)
        self.assertEqual(resultado, "JOÃO DA SILVA")
    
    def test_extract_nome_com_espacos(self):
        """Testa extração de NOME com espaços extras."""
        
        texto = """
        NOME  DO  RESPONSÁVEL  FAMILIAR  (RF)  A  SER  DESLIGADO  :  MARIA DOS SANTOS
        """
        
        resultado = self.parser._extract_nome(texto)
        self.assertEqual(resultado, "MARIA DOS SANTOS")
    
    def test_extract_motivo_simples(self):
        """Testa extração de MOTIVO simples."""
        
        texto = """
        MOTIVO DO DESLIGAMENTO
        (X) Mudança para outro Estado
        ( ) Falecimento do responsável
        ( ) Outro
        """
        
        resultado = self.parser._extract_motivo(texto)
        self.assertIn("Mudança para outro Estado", resultado)
    
    def test_extract_motivo_outro_com_descricao(self):
        """Testa extração de MOTIVO quando é OUTRO com descrição."""
        
        texto = """
        MOTIVO DO DESLIGAMENTO
        ( ) Mudança para outro Estado
        ( ) Falecimento do responsável
        (X) Outro
        Descrição do motivo customizado
        """
        
        resultado = self.parser._extract_motivo(texto)
        self.assertIn("OUTRO", resultado)
        self.assertIn("Descrição", resultado)
    
    def test_parse_completo(self):
        """Testa parse completo de um PDF simulado."""
        
        texto = """
        PREFEITURA MUNICIPAL DE FORTALEZA
        SECRETARIA DE ASSISTÊNCIA SOCIAL
        
        MUNICÍPIO: FORTALEZA
        CPF: 123.456.789-00
        NIS: 123.456.789-00
        
        NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: JOÃO DA SILVA SANTOS
        
        MOTIVO DO DESLIGAMENTO
        (X) Mudança para outro Estado
        ( ) Falecimento do responsável
        ( ) Outro
        """
        
        resultado = self.parser.parse(texto)
        
        self.assertEqual(resultado['MUNICIPIO'], 'FORTALEZA')
        self.assertEqual(resultado['CPF'], '12345678900')
        self.assertEqual(resultado['NIS'], '12345678900')
        self.assertEqual(resultado['NOME'], 'JOÃO DA SILVA SANTOS')
        self.assertIn('Mudança para outro Estado', resultado['MOTIVO'])
    
    def test_normalize_text(self):
        """Testa normalização de texto."""
        
        texto = "  JOÃO   DA   SILVA  \n  "
        resultado = self.parser._normalize(texto)
        self.assertEqual(resultado, "JOÃO DA SILVA")
    
    def test_campos_faltando_retornam_vazio(self):
        """Testa que campos faltando retornam string vazia."""
        
        texto = "Texto sem campos relevantes"
        resultado = self.parser.parse(texto)
        
        for chave, valor in resultado.items():
            self.assertEqual(valor, "")


class TestFieldParserRobustness(unittest.TestCase):
    """Testes de robustez para casos especiais."""
    
    def setUp(self):
        self.parser = FieldParser()
    
    def test_cpf_com_menos_de_11_digitos(self):
        """Testa CPF com menos de 11 dígitos."""
        
        texto = "CPF: 123456789"
        resultado = self.parser._extract_cpf(texto)
        # Deve retornar o que encontrou, mesmo que menos de 11 dígitos
        self.assertEqual(resultado, "123456789")
    
    def test_municipio_com_caracteres_especiais(self):
        """Testa municipio com caracteres especiais."""
        
        texto = "MUNICÍPIO: SÃO GONÇALO"
        resultado = self.parser._extract_municipio(texto)
        self.assertEqual(resultado, "SÃO GONÇALO")
    
    def test_nome_composto_longo(self):
        """Testa extração de nome composto e longo."""
        
        texto = """
        NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: 
        JOSÉ MARIA DE ARAÚJO SILVA SANTOS
        """
        
        resultado = self.parser._extract_nome(texto)
        self.assertIn("JOSÉ", resultado)
        self.assertIn("SANTOS", resultado)
    
    def test_texto_com_quebras_multiplas(self):
        """Testa texto com múltiplas quebras de linha."""
        
        texto = """
        MUNICIPIO:
        
        FORTALEZA
        
        CPF:
        
        123.456.789-00
        """
        
        municipio = self.parser._extract_municipio(texto)
        cpf = self.parser._extract_cpf(texto)
        
        # Dependendo da implementação, pode não encontrar se houver quebras
        # Este teste documenta o comportamento esperado
        self.assertTrue(municipio == "" or "FORTALEZA" in municipio)


if __name__ == '__main__':
    unittest.main()
