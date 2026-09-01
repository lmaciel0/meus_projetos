"""
Arquivo com exemplos de textos de PDFs para fins de teste e validação.
Estes são dados fictícios para demonstração.
"""

# Exemplo 1: PDF com todos os campos completos
EXEMPLO_1_MUNICIPIO = "FORTALEZA"
EXEMPLO_1_CPF = "12345678900"
EXEMPLO_1_NIS = "12345678901"
EXEMPLO_1_NOME = "JOÃO DA SILVA SANTOS"
EXEMPLO_1_MOTIVO = "Mudança para outro Estado"

EXEMPLO_PDF_TEXTO_1 = """
SOLICITAÇÃO DE DESLIGAMENTO
BENEFICIÁRIO DO CARTÃO MAIS INFÂNCIA CEARÁ

MUNICÍPIO: FORTALEZA

CPF: 123.456.789-00
NIS: 123.456.789-01

NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO:
JOÃO DA SILVA SANTOS

DATA DA SOLICITAÇÃO: 15/01/2024

MOTIVO DO DESLIGAMENTO

Escolha uma das opções abaixo:

( ) Transferência de guarda
( ) Morte do beneficiário
(X) Mudança para outro Estado
( ) Desistência voluntária
( ) OUTRO (Especifique): ___________________

Assinado em: ____/____/______
"""

# Exemplo 2: PDF com OUTRO como motivo
EXEMPLO_2_MOTIVO = "OUTRO: Família se mudou para outro município"

EXEMPLO_PDF_TEXTO_2 = """
SOLICITAÇÃO DE DESLIGAMENTO
BENEFICIÁRIO DO CARTÃO MAIS INFÂNCIA CEARÁ

MUNICÍPIO: MARACANAÚ

CPF: 098.765.432-10
NIS: 098.765.432-11

NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO:
MARIA DOS SANTOS OLIVEIRA

DATA DA SOLICITAÇÃO: 10/02/2024

MOTIVO DO DESLIGAMENTO

Escolha uma das opções abaixo:

( ) Transferência de guarda
( ) Morte do beneficiário
( ) Mudança para outro Estado
( ) Desistência voluntária
(X) OUTRO (Especifique): Família se mudou para outro município

Assinado em: ____/____/______
"""

# Exemplo 3: PDF com CPF/NIS iniciados com zero
EXEMPLO_3_CPF = "00123456789"
EXEMPLO_3_NIS = "00198765432"

EXEMPLO_PDF_TEXTO_3 = """
SOLICITAÇÃO DE DESLIGAMENTO

MUNICÍPIO: CAUCAIA

CPF: 001.234.567-89
NIS: 001.987.654-32

NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO:
PEDRO COSTA

MOTIVO DO DESLIGAMENTO

(X) Transferência de guarda
"""

# Exemplo 4: PDF incompleto (faltam campos)
EXEMPLO_PDF_TEXTO_4 = """
SOLICITAÇÃO DE DESLIGAMENTO

MUNICÍPIO: AQUIRAZ

CPF: 555.555.555-55

DATA: 20/03/2024
"""

# Exemplo 5: PDF com caracteres especiais
EXEMPLO_5_NOME = "JOSÉ JOÃO SÃO CARLOS"
EXEMPLO_5_MUNICIPIO = "SÃO GONÇALO DO AMARANTE"

EXEMPLO_PDF_TEXTO_5 = """
SOLICITAÇÃO DE DESLIGAMENTO

MUNICÍPIO: SÃO GONÇALO DO AMARANTE

CPF: 111.222.333-44
NIS: 111.222.333-45

NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO:
JOSÉ JOÃO SÃO CARLOS

MOTIVO DO DESLIGAMENTO

(X) Desistência voluntária
"""

# Dados esperados para validação
DADOS_ESPERADOS_1 = {
    'MUNICIPIO': 'FORTALEZA',
    'CPF': '12345678900',
    'NIS': '12345678901',
    'NOME': 'JOÃO DA SILVA SANTOS',
    'MOTIVO': 'Mudança para outro Estado',
    'ARQUIVO_ORIGEM': 'exemplo_1.pdf',
    'STATUS_EXTRACAO': 'OK'
}

DADOS_ESPERADOS_2 = {
    'MUNICIPIO': 'MARACANAÚ',
    'CPF': '09876543210',
    'NIS': '09876543211',
    'NOME': 'MARIA DOS SANTOS OLIVEIRA',
    'MOTIVO': 'OUTRO: Família se mudou para outro município',
    'ARQUIVO_ORIGEM': 'exemplo_2.pdf',
    'STATUS_EXTRACAO': 'OK'
}

DADOS_ESPERADOS_3 = {
    'MUNICIPIO': 'CAUCAIA',
    'CPF': '00123456789',
    'NIS': '00198765432',
    'NOME': 'PEDRO COSTA',
    'MOTIVO': 'Transferência de guarda',
    'ARQUIVO_ORIGEM': 'exemplo_3.pdf',
    'STATUS_EXTRACAO': 'OK'
}

# PDF com campos faltando = REVISAR
DADOS_ESPERADOS_4 = {
    'MUNICIPIO': 'AQUIRAZ',
    'CPF': '55555555555',
    'NIS': '',
    'NOME': '',
    'MOTIVO': '',
    'ARQUIVO_ORIGEM': 'exemplo_4.pdf',
    'STATUS_EXTRACAO': 'REVISAR'  # Faltam campos
}

DADOS_ESPERADOS_5 = {
    'MUNICIPIO': 'SÃO GONÇALO DO AMARANTE',
    'CPF': '11122233344',
    'NIS': '11122233345',
    'NOME': 'JOSÉ JOÃO SÃO CARLOS',
    'MOTIVO': 'Desistência voluntária',
    'ARQUIVO_ORIGEM': 'exemplo_5.pdf',
    'STATUS_EXTRACAO': 'OK'
}

# Lista de todos os exemplos
EXEMPLOS_TEXTO = [
    EXEMPLO_PDF_TEXTO_1,
    EXEMPLO_PDF_TEXTO_2,
    EXEMPLO_PDF_TEXTO_3,
    EXEMPLO_PDF_TEXTO_4,
    EXEMPLO_PDF_TEXTO_5,
]

EXEMPLOS_DADOS_ESPERADOS = [
    DADOS_ESPERADOS_1,
    DADOS_ESPERADOS_2,
    DADOS_ESPERADOS_3,
    DADOS_ESPERADOS_4,
    DADOS_ESPERADOS_5,
]

# Compatibilidade com nomes anteriores
EXEMPLO_PDF_TEXTO = EXEMPLO_PDF_TEXTO_1
DADOS_ESPERADOS_1_DICT = DADOS_ESPERADOS_1
