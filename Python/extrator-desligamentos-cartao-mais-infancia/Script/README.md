# Leitor de Desligamentos - Cartão Mais Infância Ceará (CMIC)

Ferramenta Python para extrair dados de PDFs de desligamento do Cartão Mais Infância Ceará e exportar para XLSX e CSV.

## 🎯 Funcionalidades

- **Extração de dados** de PDFs de desligamento com suporte a:
  - Texto nativo (pdfplumber)
  - OCR para PDFs escaneados (pytesseract + pdf2image)
- **Campos extraídos**:
  - MUNICIPIO
  - CPF (com preservação de zeros à esquerda)
  - NIS (com preservação de zeros à esquerda)
  - NOME DO RESPONSÁVEL
  - MOTIVO DO DESLIGAMENTO
- **Exportação**:
  - XLSX com cabeçalho congelado, filtro automático e formatação
  - CSV com separador `;` e encoding UTF-8
- **Auditoria**:
  - Coluna `ARQUIVO_ORIGEM` para rastreabilidade
  - Coluna `STATUS_EXTRACAO` para identificar registros que precisam revisão
- **CLI** simples e intuitiva
- **Relatório** de processamento no terminal

## 📋 Pré-requisitos

- Python 3.12 ou superior
- pip (gerenciador de pacotes Python)

### Dependências do Sistema (para OCR)

Se deseja usar OCR para PDFs escaneados, instale o Tesseract OCR:

**Windows (usando Chocolatey):**
```bash
choco install tesseract -y
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install tesseract-ocr
```

**macOS (usando Homebrew):**
```bash
brew install tesseract
```

> **Nota**: A extração de texto nativo funciona sem OCR. OCR é usada apenas como fallback para PDFs scaneados.

## 🚀 Instalação

### 1. Clone ou baixe este repositório

```bash
git clone <url-do-repositorio>
cd leitor_desligamentos_cmic
```

### 2. Crie um ambiente virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 💻 Uso

### Sintaxe Básica

```bash
python main.py --entrada <pasta_com_pdfs> --saida <pasta_de_saida> [--formato ambos|xlsx|csv]
```

### Exemplos

**Processar PDFs e exportar para ambos os formatos (padrão):**
```bash
python main.py --entrada ./pdfs --saida ./resultado
```

**Exportar apenas para XLSX:**
```bash
python main.py --entrada ./pdfs --saida ./resultado --formato xlsx
```

**Exportar apenas para CSV:**
```bash
python main.py --entrada ./pdfs --saida ./resultado --formato csv
```

**Com caminhos absolutos:**
```bash
python main.py --entrada "C:\Users\usuario\Desktop\pdfs" --saida "C:\Users\usuario\Desktop\resultado"
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição | Padrão |
|-----------|-------------|-----------|--------|
| `--entrada` | ✅ Sim | Pasta contendo os PDFs a processar | - |
| `--saida` | ✅ Sim | Pasta onde salvar os arquivos exportados | - |
| `--formato` | ❌ Não | Formato de exportação: `ambos`, `xlsx` ou `csv` | `ambos` |

## 📊 Saída

### Arquivo XLSX

- **Nome**: `desligamentos_YYYYMMDD_HHMMSS.xlsx`
- **Características**:
  - Cabeçalho congelado na primeira linha
  - Filtro automático em todas as colunas
  - CPF e NIS formatados como texto (preserva zeros à esquerda)
  - Colunas com largura otimizada
  - Cabeçalho em azul com texto branco

### Arquivo CSV

- **Nome**: `desligamentos_YYYYMMDD_HHMMSS.csv`
- **Características**:
  - Separador: `;` (ponto-e-vírgula)
  - Encoding: UTF-8
  - Todos os campos com aspas
  - Compatível com Excel

### Colunas na Exportação

**Colunas principais** (também no CSV):
- `MUNICIPIO` - Município extraído do PDF
- `CPF` - CPF do responsável (11 dígitos, preserva zeros)
- `NIS` - NIS do responsável (preserva zeros à esquerda)
- `NOME` - Nome do responsável familiar
- `MOTIVO` - Motivo do desligamento

**Colunas de auditoria** (apenas no XLSX):
- `ARQUIVO_ORIGEM` - Nome do arquivo PDF de origem
- `STATUS_EXTRACAO` - Status da extração (`OK` ou `REVISAR - motivo`)

## 📈 Relatório de Processamento

Após o processamento, você verá um relatório no terminal:

```
============================================================
RESUMO DO PROCESSAMENTO
============================================================
Total de arquivos processados: 42
Extrações bem-sucedidas:       40
Extrações que exigem revisão:  2
Erros ao processar:            0
============================================================

ARQUIVOS COM ERRO:
  - documento_03.pdf: Nenhum texto extraído
```

## 🧪 Testes

Para executar os testes unitários:

```bash
# Executar todos os testes
pytest

# Executar com coverage
pytest --cov=. tests/

# Executar teste específico
pytest tests/test_field_parser.py::TestFieldParser::test_extract_cpf_preserva_zeros -v
```

### Estrutura de Testes

- `tests/test_field_parser.py` - Testes para extração de campos
  - Testes de normalização
  - Testes de extração individual de cada campo
  - Testes de casos especiais (acentos, zero à esquerda, etc.)
  - Testes de robustez

## 🏗️ Estrutura do Projeto

```
leitor_desligamentos_cmic/
├── main.py                    # Script principal - CLI
├── pdf_extraction.py          # Extração de texto de PDFs (pdfplumber + OCR)
├── field_parser.py            # Parser de campos específicos
├── export_handler.py          # Exportação para XLSX e CSV
├── requirements.txt           # Dependências Python
├── .gitignore                 # Configuração Git
├── README.md                  # Este arquivo
└── tests/
    ├── __init__.py
    └── test_field_parser.py   # Testes unitários
```

## 🔧 Módulos

### `pdf_extraction.py`

Responsável pela extração de texto de PDFs.

**Classe principal**: `PDFExtractor`

```python
from pdf_extraction import PDFExtractor

extrator = PDFExtractor()
texto = extrator.extract_text('documento.pdf')
```

**Métodos**:
- `extract_text(pdf_path)` - Extrai texto do PDF (tenta pdfplumber primeiro, depois OCR)
- `normalize_text(text)` - Normaliza espaços e quebras de linha

### `field_parser.py`

Responsável pela interpretação dos campos do texto.

**Classe principal**: `FieldParser`

```python
from field_parser import FieldParser

parser = FieldParser()
dados = parser.parse(texto)
# Retorna dicionário com chaves: MUNICIPIO, CPF, NIS, NOME, MOTIVO
```

**Métodos públicos**:
- `parse(texto)` - Extrai todos os campos e retorna dicionário

**Métodos privados** (podem ser usado para parse individual):
- `_extract_municipio(texto)`
- `_extract_cpf(texto)`
- `_extract_nis(texto)`
- `_extract_nome(texto)`
- `_extract_motivo(texto)`

### `export_handler.py`

Responsável pela exportação de dados.

**Classe principal**: `ExportHandler`

```python
from export_handler import ExportHandler

exportador = ExportHandler()
exportador.export_xlsx(dados, 'saida.xlsx')
exportador.export_csv(dados, 'saida.csv')
```

**Métodos**:
- `export_xlsx(dados, output_path)` - Exporta para XLSX formatado
- `export_csv(dados, output_path)` - Exporta para CSV com `;`

## ⚙️ Configuração Avançada

### Desabilitar OCR

Se não quer usar OCR e quer ganhar velocidade:

```python
from pdf_extraction import PDFExtractor

extrator = PDFExtractor(ocr_enabled=False)
texto = extrator.extract_text('documento.pdf')
```

### Processar PDFs Recursivamente

O script já processa PDFs em subpastas. Se seus PDFs estão em:
```
pdfs/
├── 2024/
│   ├── documento1.pdf
│   └── documento2.pdf
└── documento3.pdf
```

Basta usar:
```bash
python main.py --entrada ./pdfs --saida ./resultado
```

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'pdfplumber'"

**Solução**: Instale as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "Tesseract is not installed or is not in your PATH"

**Solução**: Instale o Tesseract OCR (veja Pré-requisitos acima)

### OCR muito lento

**Solução**: Se não precisa de OCR, desabilite-o:
```python
extrator = PDFExtractor(ocr_enabled=False)
```

### CPF/NIS perdendo zeros à esquerda no Excel

**Solução**: O arquivo XLSX já formata CPF e NIS como texto automaticamente. Se abrir em outro programa, certifique-se de abrir como texto.

### Campos não encontrados em PDFs válidos

Possíveis causas:
1. PDF é imagem (sem texto nativo) - instale Tesseract OCR
2. Formatação diferente do esperado - edite os padrões regex em `field_parser.py`
3. Caracteres especiais ou quebras inesperadas - verifique os logs

Registros com campos faltando serão marcados como `REVISAR` automaticamente.

## 📝 Exemplo Completo

```bash
# 1. Preparar pasta com PDFs
mkdir pdfs
# (copiar seus PDFs para ./pdfs)

# 2. Criar pasta de saída
mkdir resultado

# 3. Executar o processamento
python main.py --entrada ./pdfs --saida ./resultado --formato ambos

# 4. Verificar resultados
# Arquivos gerados:
# - resultado/desligamentos_20240115_143022.xlsx
# - resultado/desligamentos_20240115_143022.csv
```

## 📄 Formato dos Dados Esperados

O script espera PDFs com estrutura semelhante a:

```
PREFEITURA MUNICIPAL DE [CIDADE]
SECRETARIA DE ASSISTÊNCIA SOCIAL

MUNICÍPIO: FORTALEZA
CPF: 123.456.789-00
NIS: 123.456.789-00

NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: JOÃO DA SILVA

MOTIVO DO DESLIGAMENTO
(X) Mudança para outro Estado
( ) Falecimento do responsável
( ) Outro
```

Se seus PDFs têm estrutura diferente, edite os padrões regex em `field_parser.py`.

## 🔐 Privacidade e Segurança

- O script processa PDFs localmente - nenhum dado é enviado para servidores externos
- Arquivos CSV e XLSX são salvos localmente
- Recomenda-se não compartilhar os arquivos de saída contendo dados sensíveis

## 📝 Licença

Este projeto é fornecido como está, para uso na Prefeitura Municipal de Fortaleza.

## 🤝 Contribuição

Para reportar problemas ou sugerir melhorias, abra uma issue ou entre em contato.

## 📞 Suporte

Para dúvidas ou problemas, consulte a seção de Troubleshooting ou verifique os logs gerados pelo script.

---

**Última atualização**: 2024-01-15  
**Versão**: 1.0.0
