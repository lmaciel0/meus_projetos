# Exemplos de Uso - Leitor de Desligamentos CMIC

## 1. Uso Básico via CLI

### Exemplo 1: Processar PDFs e exportar para ambos os formatos

```bash
python main.py --entrada ./pdfs --saida ./resultado
```

**Saída esperada:**
- `resultado/desligamentos_20240115_143022.xlsx`
- `resultado/desligamentos_20240115_143022.csv`

### Exemplo 2: Exportar apenas para XLSX

```bash
python main.py --entrada ./pdfs --saida ./resultado --formato xlsx
```

### Exemplo 3: Exportar apenas para CSV

```bash
python main.py --entrada ./pdfs --saida ./resultado --formato csv
```

## 2. Uso Programático em Python

### Exemplo 1: Processar e exportar

```python
from main import DesligamentoProcessor

# Criar processador
processor = DesligamentoProcessor('./pdfs', './resultado')

# Processar PDFs
stats = processor.process()

# Exportar resultados
processor.export(stats, ['xlsx', 'csv'])

# Exibir resumo
processor.print_summary(stats)
```

### Exemplo 2: Usar a função auxiliar

```python
from utils import processar_desligamentos

stats = processar_desligamentos(
    pasta_entrada='./pdfs',
    pasta_saida='./resultado',
    formato='ambos',
    verboso=True
)

print(f"Sucesso: {stats['sucesso']}")
print(f"Revisão: {stats['revisar']}")
```

### Exemplo 3: Obter dados sem exportar

```python
from utils import obter_dados_apenas

dados = obter_dados_apenas('./pdfs')

# Processar dados em memória
for registro in dados:
    print(f"{registro['NOME']} - {registro['MUNICIPIO']}")
    
    if registro['STATUS_EXTRACAO'] != 'OK':
        print(f"  ⚠️  {registro['STATUS_EXTRACAO']}")
```

### Exemplo 4: Extração individual de um PDF

```python
from pdf_extraction import PDFExtractor
from field_parser import FieldParser

# Extrair texto
extrator = PDFExtractor()
texto = extrator.extract_text('documento.pdf')

# Parse de campos
parser = FieldParser()
dados = parser.parse(texto)

print(f"Município: {dados['MUNICIPIO']}")
print(f"CPF: {dados['CPF']}")
print(f"Nome: {dados['NOME']}")
print(f"Motivo: {dados['MOTIVO']}")
```

### Exemplo 5: Exportar dados customizados

```python
from export_handler import ExportHandler

exportador = ExportHandler()

# Dados customizados
dados = [
    {
        'MUNICIPIO': 'FORTALEZA',
        'CPF': '12345678900',
        'NIS': '12345678900',
        'NOME': 'JOÃO DA SILVA',
        'MOTIVO': 'Mudança para outro Estado',
        'ARQUIVO_ORIGEM': 'documento_01.pdf',
        'STATUS_EXTRACAO': 'OK'
    }
]

# Exportar
exportador.export_xlsx(dados, 'saida.xlsx')
exportador.export_csv(dados, 'saida.csv')
```

## 3. Casos de Uso Avançados

### Exemplo 1: Processar com OCR desabilitado (mais rápido)

```python
from pdf_extraction import PDFExtractor

# Desabilitar OCR para melhor performance
extrator = PDFExtractor(ocr_enabled=False)
texto = extrator.extract_text('documento.pdf')
```

### Exemplo 2: Processar múltiplas pastas

```python
from pathlib import Path
from main import DesligamentoProcessor

pastas = ['./pdfs/2024_01', './pdfs/2024_02', './pdfs/2024_03']

for pasta in pastas:
    processor = DesligamentoProcessor(pasta, f'./resultado/{Path(pasta).name}')
    stats = processor.process()
    processor.export(stats, ['xlsx'])
    processor.print_summary(stats)
```

### Exemplo 3: Filtrar registros por status

```python
from utils import obter_dados_apenas

dados = obter_dados_apenas('./pdfs')

# Apenas registros com sucesso
sucesso = [d for d in dados if d['STATUS_EXTRACAO'] == 'OK']

# Apenas registros que precisam revisão
revisar = [d for d in dados if d['STATUS_EXTRACAO'] != 'OK']

print(f"Total com sucesso: {len(sucesso)}")
print(f"Total para revisar: {len(revisar)}")
```

### Exemplo 4: Integração com banco de dados

```python
from utils import obter_dados_apenas
import sqlite3

dados = obter_dados_apenas('./pdfs')

# Conectar ao banco
conn = sqlite3.connect('desligamentos.db')
cursor = conn.cursor()

# Criar tabela
cursor.execute('''
    CREATE TABLE IF NOT EXISTS desligamentos (
        id INTEGER PRIMARY KEY,
        municipio TEXT,
        cpf TEXT,
        nis TEXT,
        nome TEXT,
        motivo TEXT,
        arquivo_origem TEXT,
        status TEXT
    )
''')

# Inserir dados
for d in dados:
    cursor.execute('''
        INSERT INTO desligamentos 
        (municipio, cpf, nis, nome, motivo, arquivo_origem, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        d['MUNICIPIO'],
        d['CPF'],
        d['NIS'],
        d['NOME'],
        d['MOTIVO'],
        d['ARQUIVO_ORIGEM'],
        d['STATUS_EXTRACAO']
    ))

conn.commit()
conn.close()
```

### Exemplo 5: Validação customizada de dados

```python
from utils import obter_dados_apenas

def validar_cpf(cpf):
    """Valida CPF (simples)"""
    return len(cpf) == 11 and cpf.isdigit()

def validar_nis(nis):
    """Valida NIS (simples)"""
    return len(nis) >= 11 and nis.isdigit()

dados = obter_dados_apenas('./pdfs')

for d in dados:
    erros = []
    
    if not validar_cpf(d['CPF']):
        erros.append(f"CPF inválido: {d['CPF']}")
    
    if not validar_nis(d['NIS']):
        erros.append(f"NIS inválido: {d['NIS']}")
    
    if not d['NOME'].strip():
        erros.append("Nome vazio")
    
    if erros:
        print(f"❌ {d['ARQUIVO_ORIGEM']}")
        for erro in erros:
            print(f"   - {erro}")
    else:
        print(f"✓ {d['ARQUIVO_ORIGEM']}: OK")
```

## 4. Testes

### Executar todos os testes

```bash
pytest
```

### Executar com output detalhado

```bash
pytest -v
```

### Executar com coverage

```bash
pytest --cov=. tests/
```

### Executar teste específico

```bash
pytest tests/test_field_parser.py::TestFieldParser::test_extract_cpf_preserva_zeros -v
```

## 5. Troubleshooting

### Verificar se as dependências estão instaladas

```python
import sys

try:
    import pdfplumber
    print("✓ pdfplumber instalado")
except ImportError:
    print("✗ pdfplumber não instalado")

try:
    import pandas
    print("✓ pandas instalado")
except ImportError:
    print("✗ pandas não instalado")

try:
    import pytesseract
    print("✓ pytesseract instalado")
except ImportError:
    print("✗ pytesseract não instalado")
```

### Testar extração de um PDF específico

```python
from pdf_extraction import PDFExtractor
from field_parser import FieldParser

extrator = PDFExtractor()
parser = FieldParser()

# Processar PDF
texto = extrator.extract_text('documento.pdf')
dados = parser.parse(texto)

# Mostrar resultado
for chave, valor in dados.items():
    print(f"{chave:15} : {valor}")
```

### Verificar configuração do Tesseract (OCR)

```python
try:
    import pytesseract
    print(f"Tesseract path: {pytesseract.pytesseract.pytesseract_cmd}")
except Exception as e:
    print(f"Erro ao verificar Tesseract: {e}")
```

---

Para mais informações, consulte o README.md
