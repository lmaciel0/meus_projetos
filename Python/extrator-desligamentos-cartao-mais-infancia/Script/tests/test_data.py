"""
Dados de teste e fixtures para testes unitários.
"""

# Exemplo de PDF simulado para testes
EXEMPLO_PDF_TEXTO = """
PREFEITURA MUNICIPAL DE FORTALEZA
SECRETARIA DE ASSISTÊNCIA SOCIAL
CARTÃO MAIS INFÂNCIA CEARÁ

MUNICÍPIO: FORTALEZA
CPF: 123.456.789-00
NIS: 123.456.789-00

NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: JOÃO SILVA SANTOS

DATA DO DESLIGAMENTO: 15/01/2024

MOTIVO DO DESLIGAMENTO
(X) Mudança para outro Estado
( ) Falecimento do responsável
( ) Mudança de endereço
( ) Solicitação do responsável
( ) Outro: Por favor descrever

OBSERVAÇÕES:
Desligamento solicitado pelo próprio responsável.

Data: 15/01/2024
Responsável: Maria Silva
Assinatura: ___________________
"""

# Exemplo de PDF com OUTRO motivo
EXEMPLO_PDF_OUTRO_MOTIVO = """
MUNICÍPIO: CAUCAIA
CPF: 098.765.432-10
NIS: 987.654.321-00

NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: MARIA DOS SANTOS

MOTIVO DO DESLIGAMENTO
( ) Mudança para outro Estado
( ) Falecimento do responsável
( ) Mudança de endereço
(X) Outro
Mudança para outro programa social com benefício maior
"""

# Exemplo de PDF com campos faltando (vai gerar REVISAR)
EXEMPLO_PDF_INCOMPLETO = """
MUNICÍPIO: MARACANAÚ
CPF: 111.222.333-44

NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: JOSÉ PEREIRA

MOTIVO DO DESLIGAMENTO
(X) Mudança para outro Estado
"""

# Exemplo de dados esperados após parse
DADOS_ESPERADOS_1 = {
    'MUNICIPIO': 'FORTALEZA',
    'CPF': '12345678900',
    'NIS': '12345678900',
    'NOME': 'JOÃO SILVA SANTOS',
    'MOTIVO': 'Mudança para outro Estado'
}

DADOS_ESPERADOS_2 = {
    'MUNICIPIO': 'CAUCAIA',
    'CPF': '09876543210',
    'NIS': '98765432100',
    'NOME': 'MARIA DOS SANTOS',
    'MOTIVO': 'OUTRO: Mudança para outro programa social com benefício maior'
}

DADOS_ESPERADOS_3 = {
    'MUNICIPIO': 'MARACANAÚ',
    'CPF': '11122233344',
    'NIS': '',
    'NOME': 'JOSÉ PEREIRA',
    'MOTIVO': 'Mudança para outro Estado'
}
