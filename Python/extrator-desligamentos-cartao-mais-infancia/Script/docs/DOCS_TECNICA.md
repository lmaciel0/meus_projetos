# Documentação Técnica - Leitor de Desligamentos CMIC

## Índice

1. [Arquitetura](#arquitetura)
2. [Fluxo de Processamento](#fluxo-de-processamento)
3. [Módulos](#módulos)
4. [Padrões de Regex](#padrões-de-regex)
5. [Tratamento de Erros](#tratamento-de-erros)
6. [Performance](#performance)
7. [Segurança](#segurança)

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI (main.py)                         │
├─────────────────────────────────────────────────────────────┤
│                   DesligamentoProcessor                      │
├──────────────────────┬──────────────────────┬────────────────┤
│   PDFExtractor       │   FieldParser        │ ExportHandler  │
│                      │                      │                │
│ - pdfplumber         │ - Regex patterns     │ - XLSX export  │
│ - OCR (fallback)     │ - Field validation   │ - CSV export   │
│ - Text normalization │ - Data cleaning      │ - Formatting   │
└──────────────────────┴──────────────────────┴────────────────┘
```

## Fluxo de Processamento

```
┌─────────────────────────────────────────────────┐
│  1. Inicializar DesligamentoProcessor           │
│     (input_dir, output_dir)                     │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  2. Encontrar todos os PDFs na pasta            │
│     (glob *.pdf e recursivamente)               │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  3. Para cada PDF:                              │
│     a) PDFExtractor.extract_text()              │
│        - Tentar pdfplumber                      │
│        - Fallback para OCR                      │
│        - Normalizar texto                       │
│     b) FieldParser.parse()                      │
│        - Extrair MUNICIPIO                      │
│        - Extrair CPF                            │
│        - Extrair NIS                            │
│        - Extrair NOME                           │
│        - Extrair MOTIVO                         │
│     c) Determinar STATUS_EXTRACAO               │
│        - OK se todos campos encontrados         │
│        - REVISAR se faltam campos               │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  4. Compilar estatísticas                       │
│     - Total processados                         │
│     - Sucessos                                  │
│     - Revisões necessárias                      │
│     - Erros                                     │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  5. Exportar dados                              │
│     - ExportHandler.export_xlsx()               │
│     - ExportHandler.export_csv()                │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  6. Exibir resumo no terminal                   │
└─────────────────────────────────────────────────┘
```

## Módulos

### 1. main.py

**Responsabilidade**: Orquestração e CLI

**Classe Principal**: `DesligamentoProcessor`

```python
class DesligamentoProcessor:
    def __init__(self, input_dir: Path, output_dir: Path)
    def process(self) -> Dict  # Processa PDFs
    def export(self, stats: Dict, formatos: List[str]) -> None  # Exporta
    def print_summary(self, stats: Dict) -> None  # Exibe resumo
```

**Métodos Private**:
- `_get_timestamp()`: Gera timestamp para nomes de arquivo

**Fluxo**:
1. Valida pasta de entrada
2. Encontra todos PDFs
3. Para cada PDF, processa e parse
4. Classifica como OK ou REVISAR
5. Retorna estatísticas
6. Exporta se houver dados

### 2. pdf_extraction.py

**Responsabilidade**: Extração de texto de PDFs

**Classe Principal**: `PDFExtractor`

```python
class PDFExtractor:
    def __init__(self, ocr_enabled: bool = True)
    def extract_text(self, pdf_path: str) -> str
    @staticmethod
    def normalize_text(text: str) -> str
```

**Métodos Private**:
- `_extract_with_pdfplumber(pdf_path)`: Usa pdfplumber
- `_extract_with_ocr(pdf_path)`: Usa pytesseract + pdf2image

**Estratégia de Extração**:
1. Tenta pdfplumber (nativo)
2. Se vazio, tenta OCR
3. Normaliza espaços e quebras de linha

### 3. field_parser.py

**Responsabilidade**: Interpretação de campos específicos

**Classe Principal**: `FieldParser`

```python
class FieldParser:
    def parse(self, texto: str) -> Dict[str, str]
```

**Métodos Private** (um para cada campo):
- `_extract_municipio(texto)`
- `_extract_cpf(texto)`
- `_extract_nis(texto)`
- `_extract_nome(texto)`
- `_extract_motivo(texto)`

**Métodos Auxiliares**:
- `_normalize(text)`: Remove espaços extras
- `_remove_accents(text)`: Remove acentos (para busca)

### 4. export_handler.py

**Responsabilidade**: Exportação de dados para XLSX e CSV

**Classe Principal**: `ExportHandler`

```python
class ExportHandler:
    def export_xlsx(self, dados: List[Dict], output_path: str) -> None
    def export_csv(self, dados: List[Dict], output_path: str) -> None
```

**Métodos Private**:
- `_prepare_dataframe()`: Prepara DataFrame
- `_format_xlsx()`: Formata arquivo XLSX

**Formatação XLSX**:
- Cabeçalho congelado (freeze_panes)
- Filtro automático (auto_filter)
- CPF/NIS como texto (@)
- Cabeçalho colorido (azul + branco)
- Largura otimizada

## Padrões de Regex

### MUNICIPIO

```regex
MUNICÍPIO\s*:\s*([^\n]+)
```

Encontra: `MUNICÍPIO: <valor>`

**Tratamento**:
- Remove espaços extras
- Remove números no final

### CPF

```regex
CPF\s*:\s*([^\n]+)
```

Encontra: `CPF: <valor>`

**Tratamento**:
- Extrai apenas dígitos
- Preserva zeros à esquerda
- Retorna primeiros 11 dígitos

### NIS

```regex
NIS\s*:\s*([^\n]+)
```

Encontra: `NIS: <valor>`

**Tratamento**:
- Extrai apenas dígitos
- Preserva zeros à esquerda
- Retorna todos os dígitos

### NOME

```regex
NOME\s+DO\s+RESPONSÁVEL\s+FAMILIAR\s*\(RF\)\s+A\s+SER\s+DESLIGADO\s*:\s*([^\n]+)
```

Encontra: `NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: <valor>`

**Tratamento**:
- Remove números no final
- Normaliza espaços

### MOTIVO

```regex
MOTIVO\s+DO\s+DESLIGAMENTO(.*?)(?=\n\n|$)
```

Encontra: Seção `MOTIVO DO DESLIGAMENTO`

**Tratamento**:
- Procura por padrão (X) ou ( X ) ou (x)
- Se OUTRO, procura descrição na próxima linha
- Retorna texto completo da opção

## Tratamento de Erros

### Erros de Arquivo

| Erro | Causa | Ação |
|------|-------|------|
| `FileNotFoundError` | PDF não existe | Log e skip |
| `Nenhum texto extraído` | PDF vazio ou inválido | Marcar como REVISAR |
| Erro de OCR | Tesseract não instalado | Fallback para texto nativo |

### Erros de Exportação

| Erro | Causa | Ação |
|------|-------|------|
| `ImportError` pandas | Dependência faltando | Log e skip export |
| Pasta não existe | Saída não criada | Criar automaticamente |

### Classificação REVISAR

Registro marcado como `REVISAR` quando:
- Falta MUNICIPIO
- Falta CPF
- Falta NIS
- Falta NOME
- Falta MOTIVO
- Ambiguidade em MOTIVO

## Performance

### Otimizações

1. **Processamento em memória**: Não carrega arquivo completo de uma vez
2. **Regex compilado**: Padrões compilados para velocidade
3. **Suporte a múltiplas páginas**: Processa todas as páginas em um PDFPlumber session
4. **OCR opcional**: Desabilitar OCR para performance se não necessário

### Benchmarks (Indicativos)

| Tipo | Tempo Médio |
|------|-------------|
| PDF com texto nativo (1 pág) | ~50ms |
| PDF com OCR (1 pág) | ~500ms |
| Exportação XLSX (1000 registros) | ~200ms |
| Exportação CSV (1000 registros) | ~50ms |

### Escalabilidade

- Processamento de PDFs é sequencial (por arquivo)
- Possível paralelizar com `multiprocessing` (futuro)
- Limite atual: Testado com até 1000 PDFs
- Para mais, considerar paralelização ou processamento em chunks

## Segurança

### Considerações

1. **Dados Sensíveis**: Projeto processa dados sensíveis (CPF, NIS)
   - Processar localmente apenas
   - Não enviar para servidores
   - Proteger arquivo de saída

2. **Injeção de Código**: PDFs processados como dados, não como código
   - Regex usado apenas para busca, não para execução
   - Sem `eval()` ou `exec()`

3. **Path Traversal**: Entrada de usuário (--entrada, --saida)
   - Validar paths
   - Usar `Path` do pathlib (seguro)

4. **Autorização**: Sem autenticação necessária
   - Projeto é CLI local
   - Arquivo acesso baseado em sistema operacional

5. **Criptografia**: Não implementada (dados em texto claro em CSVs)
   - XLSX é comprimido (alguma proteção)
   - Considerar criptografia para versões futuras

### Recomendações de Uso

```bash
# Definir permissões apropriadas
chmod 700 resultado/  # Apenas owner pode ler/escrever
chmod 600 resultado/*.xlsx  # Apenas owner pode ler

# Em Windows
icacls resultado /grant:r "%username%:F" /inheritance:r
```

---

## Desenvolvimento Futuro

### Melhorias Planejadas

1. **Processamento Paralelo**: Usar `concurrent.futures` para múltiplos PDFs
2. **Cache**: Armazenar PDFs processados para evitar re-processamento
3. **API REST**: Expor funcionalidade via FastAPI
4. **Web UI**: Dashboard com Streamlit ou Flask
5. **Validação Customizável**: Permitir padrões regex personalizados
6. **Relatórios**: Gerar relatórios em PDF com gráficos

### Testes

- Testes unitários: `tests/test_field_parser.py`
- Testes de integração: `tests/test_integration.py`
- Coverage target: > 80%

### Documentação

- README.md: Instruções de uso
- EXEMPLOS.md: Exemplos de código
- CONTRIBUINDO.md: Guia de contribuição
- Esta documentação técnica

---

**Versão**: 1.0.0  
**Atualizado**: 2024-01-15
