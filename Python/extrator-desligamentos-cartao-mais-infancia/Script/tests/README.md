# Testes - Leitor de Desligamentos CMIC

Este diretório contém todos os testes para o projeto.

## Estrutura

```
tests/
├── __init__.py              # Inicializador do pacote
├── test_field_parser.py     # Testes unitários do parser
├── test_integration.py      # Testes de integração
├── test_samples.py          # Exemplos de dados para testes
└── README.md                # Este arquivo
```

## Executar Testes

### Todos os testes
```bash
pytest tests/ -v
```

### Com cobertura
```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Teste específico
```bash
pytest tests/test_field_parser.py::test_extract_municipio -v
```

### Teste específico com output
```bash
pytest tests/test_field_parser.py -v -s
```

## Arquivos de Teste

### test_field_parser.py

Testa o módulo `field_parser.py` que extrai campos dos PDFs.

**Testes inclusos:**
- `test_extract_municipio*` (3 testes)
- `test_extract_cpf*` (4 testes)
- `test_extract_nis*` (3 testes)
- `test_extract_nome*` (3 testes)
- `test_extract_motivo*` (3 testes)
- `test_parse_completo` (1 teste)
- `test_campos_faltando_retornam_vazio` (1 teste)
- Testes de robustez (5+ testes)

Total: 20+ testes

**Cobertura:** ~85% do módulo field_parser.py

### test_integration.py

Testa o fluxo completo de processamento.

**Testes inclusos:**
- `TestFluxoCompleto`
  - Inicialização do processador
  - Processamento de pasta vazia
  - Field parser com dados reais
  - Exportação XLSX
  - Exportação CSV

- `TestValidacaoDados`
  - Preservação de zeros em CPF
  - Preservação de zeros em NIS
  - Campos vazios

**Cobertura:** ~60% do fluxo end-to-end

### test_samples.py

Exemplos de dados para usar em testes e prototipagem.

**Incluso:**
- 5 textos de exemplo de PDFs (EXEMPLO_PDF_TEXTO_1 até 5)
- Dados esperados para cada exemplo (DADOS_ESPERADOS_1 até 5)
- Dados com CPF/NIS iniciados com zero
- Dados com caracteres especiais
- Dados incompletos (para marcar como REVISAR)

## Dados de Teste

Os dados de teste estão em `test_samples.py` e cobrem:

1. **PDF Completo**: Todos os campos presentes
2. **PDF com OUTRO**: Motivo é OUTRO com descrição
3. **PDF com Zeros à Esquerda**: CPF/NIS começam com 0
4. **PDF Incompleto**: Faltam campos (status REVISAR)
5. **PDF com Acentos**: Caracteres especiais e acentuação

## Adicionando Novos Testes

### Template de Teste Unitário

```python
def test_nova_funcionalidade():
    """Breve descrição do teste."""
    # Arrange (Preparar)
    entrada = "dados de entrada"
    esperado = "resultado esperado"
    
    # Act (Agir)
    parser = FieldParser()
    resultado = parser._extract_campo(entrada)
    
    # Assert (Verificar)
    assert resultado == esperado
```

### Template de Teste de Integração

```python
def test_fluxo_novo():
    """Breve descrição do teste."""
    # Arrange
    processor = DesligamentoProcessor(
        str(self.entrada),
        str(self.saida)
    )
    
    # Act
    stats = processor.process()
    
    # Assert
    assert stats['total_processados'] > 0
```

## Pytest Markers

Para organizar testes:

```python
@pytest.mark.slow
def test_ocr_lento():
    # Teste demorado
    pass

@pytest.mark.skip(reason="Ainda não implementado")
def test_feature_futura():
    pass

@pytest.mark.parametrize("entrada,esperado", [
    ("001", "001"),
    ("100", "100"),
])
def test_multiplos_casos(entrada, esperado):
    assert entrada == esperado
```

Use: `pytest -m slow` ou `pytest -m "not slow"`

## Cobertura

Atual: ~70% do código

Objetivo: >80%

Ver relatório: `htmlcov/index.html` (após executar com `--cov-report=html`)

## Mock e Fixtures

### Fixtures Disponíveis

```python
@pytest.fixture
def parser():
    """Parser para uso em testes."""
    return FieldParser()

@pytest.fixture
def temp_pdfs(tmp_path):
    """Cria PDFs temporários para testes."""
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    return pdf_dir
```

### Usando Fixtures

```python
def test_com_fixture(parser):
    resultado = parser.parse("texto")
    assert resultado is not None
```

## Troubleshooting

### Tesseract não encontrado
```bash
# Windows (com Chocolatey)
choco install tesseract

# macOS
brew install tesseract

# Linux (Debian/Ubuntu)
sudo apt-get install tesseract-ocr
```

### Dependências faltando
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Teste falhando
1. Execute com verbose: `pytest -vv`
2. Mostre output: `pytest -s`
3. Abra debugger: `pytest --pdb` (ctrl+l para lista de comandos)

## CI/CD

Os testes são executados automaticamente via GitHub Actions em:
- Cada push
- Cada pull request
- Em múltiplos SOs (Linux, Windows, macOS)
- Em Python 3.12

Ver `.github/workflows/tests.yml` para configuração.

---

**Última atualização:** 2024-01-15
