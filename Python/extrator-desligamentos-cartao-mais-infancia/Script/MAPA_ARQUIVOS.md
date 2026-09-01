# 📁 Mapa de Arquivos - Leitor de Desligamentos CMIC

Guia completo de todos os arquivos do projeto e suas funções.

## 🔴 COMECE AQUI

- **[COMECE_AQUI.md](COMECE_AQUI.md)** ← Guia de 5 minutos para começar
- **[RESUMO_PROJETO.md](RESUMO_PROJETO.md)** - Visão geral completa do projeto

## 📚 Documentação Principal

### Usuários
- **[README.md](README.md)** (364 linhas)
  - Funcionalidades
  - Instalação passo-a-passo
  - Uso via CLI
  - Formato de saída
  - Troubleshooting
  - Exemplo completo

- **[EXEMPLOS.md](EXEMPLOS.md)** (276 linhas)
  - 3 exemplos de CLI
  - 5 exemplos programáticos
  - 5 exemplos avançados
  - Troubleshooting para desenvolvimento

### Desenvolvedores
- **[DOCS_TECNICA.md](DOCS_TECNICA.md)** (380+ linhas)
  - Arquitetura do projeto
  - Fluxo de processamento
  - Documentação de módulos
  - Padrões de regex
  - Tratamento de erros
  - Performance e escalabilidade
  - Considerações de segurança

- **[CONTRIBUTING.md](CONTRIBUTING.md)** (211 linhas)
  - Como reportar bugs
  - Como sugerir melhorias
  - Processo de desenvolvimento
  - Guia de estilo de código
  - Requisitos de testes
  - Padrões de documentação

## 📝 Controle de Versão

- **[CHANGELOG.md](CHANGELOG.md)** (74 linhas)
  - Histórico de versões
  - Mudanças de cada release
  - Roadmap futuro
  - v1.0.0 - Release inicial
  - Planejamento v1.1-v1.2

## 📦 Código Fonte

### Módulos Principais (5 arquivos)

1. **[main.py](main.py)** (285 linhas)
   - CLI com argparse
   - Classe DesligamentoProcessor
   - Orquestração do fluxo
   - Exibição de resumo
   - Entrada: --entrada, --saida, --formato

2. **[pdf_extraction.py](pdf_extraction.py)** (137 linhas)
   - Classe PDFExtractor
   - Estratégia dual: pdfplumber + OCR
   - Normalização de texto
   - Suporte a múltiplas páginas

3. **[field_parser.py](field_parser.py)** (218 linhas)
   - Classe FieldParser
   - 5 métodos de extração (MUNICIPIO, CPF, NIS, NOME, MOTIVO)
   - Regex patterns otimizados
   - Preservação de zeros à esquerda
   - Normalização e limpeza de dados

4. **[export_handler.py](export_handler.py)** (188 linhas)
   - Classe ExportHandler
   - Export para XLSX (com formatação)
   - Export para CSV (semicolon)
   - Formatação profissional (cabeçalho, filtros, cores)

5. **[utils.py](utils.py)** (97 linhas)
   - Interface programática
   - processar_desligamentos() - wrapper
   - obter_dados_apenas() - retorna dados sem exportar
   - Uso em scripts e integrações

### Testes (6 arquivos)

- **[tests/](tests/)**
  - **[__init__.py](tests/__init__.py)** - Inicializador do pacote
  
  - **[test_field_parser.py](tests/test_field_parser.py)** (196 linhas)
    - 20+ testes unitários
    - Cobertura: MUNICIPIO, CPF, NIS, NOME, MOTIVO
    - Testes de robustez (acentos, zeros, espaços)
  
  - **[test_integration.py](tests/test_integration.py)** (140+ linhas)
    - 5 classes de teste
    - Teste de fluxo completo
    - Validação de dados
    - Testes de export XLSX/CSV
  
  - **[test_data.py](tests/test_data.py)** (59 linhas)
    - Dados de teste fixos
    - 3 exemplos de PDF
    - Dados esperados para cada exemplo
  
  - **[test_samples.py](tests/test_samples.py)** (150+ linhas)
    - 5 exemplos completos de PDFs
    - Dados esperados para validação
    - Cobertura: campos completos, incompletos, acentos, zeros
  
  - **[README.md](tests/README.md)** (200+ linhas)
    - Guia de como executar testes
    - Descrição de cada arquivo
    - Adição de novos testes
    - Troubleshooting de testes

## ⚙️ Configuração

### Dependências
- **[requirements.txt](requirements.txt)** (23 linhas)
  - Todas as dependências do projeto
  - Versões mínimas especificadas
  - Seções: Core, Data, Dev, Docs

### Configuração Python
- **[setup.py](setup.py)** (68 linhas)
  - Metadados do pacote
  - Entry point: `leitor-desligamentos` CLI
  - Configuração de instalação via pip

- **[pytest.ini](pytest.ini)** (11 linhas)
  - Configuração de descoberta de testes
  - Marcadores customizados

- **[tox.ini](tox.ini)** (40+ linhas)
  - Ambientes de teste (py312, lint, type, format, cov)
  - Configuração de flake8
  - Ferramentas de qualidade

### Ambientes
- **[.env.example](.env.example)** (8 linhas)
  - Variáveis de ambiente exemplo
  - Config: entrada_padrao, saida_padrao, usar_ocr

- **[.gitignore](.gitignore)** (91 linhas)
  - Exclusões de versão
  - Padrões Python, IDE, OS
  - Arquivos de resultado (xlsx, csv)

## 🐳 Docker

- **[Dockerfile](Dockerfile)** (30 linhas)
  - Imagem Python 3.12-slim
  - Instalação de Tesseract para OCR
  - Volumes para /app/input e /app/output
  - Comando padrão configurado

- **[docker-compose.yml](docker-compose.yml)** (30+ linhas)
  - Orquestração Docker
  - Mapeamento de volumes (pdfs → input, resultado → output)
  - Variáveis de ambiente

- **[.dockerignore](.dockerignore)** (40+ linhas)
  - Exclusões para build Docker
  - Reduz tamanho da imagem

## 🔧 Automação

- **[Makefile](Makefile)** (80+ linhas)
  - Targets para: install, test, lint, format, run, clean
  - Docker targets: docker-build, docker-run, docker-clean
  - Targets de desenvolvimento: dev-setup, check

- **[help.bat](help.bat)** (94 linhas)
  - Scripts de ajuda para Windows
  - Comandos: help, install, test, run, lint, format

- **[help.sh](help.sh)** (110 linhas)
  - Scripts de ajuda para Linux/macOS
  - Mesmos comandos que help.bat
  - Plus: comando clean

## CI/CD

- **[.github/workflows/tests.yml](.github/workflows/tests.yml)** (60+ linhas)
  - GitHub Actions workflow
  - Roda em: Linux, Windows, macOS
  - Python 3.12
  - Lint + Tests + Coverage

## 📋 Informações Adicionais

- **[LICENSE](LICENSE)** (21 linhas)
  - Licença MIT
  - Copyright Prefeitura Municipal de Fortaleza

---

## 📊 Estatísticas

| Categoria | Quantidade |
|-----------|-----------|
| Módulos Python | 5 |
| Arquivos de Teste | 6 |
| Arquivos de Config | 8 |
| Documentação | 8 |
| Total de Arquivos | 27+ |
| Linhas de Código | ~600 |
| Linhas de Teste | ~250+ |
| Linhas de Documentação | ~2000+ |

## 🎯 Fluxo de Leitura Recomendado

### 👤 Se você quer **usar** o projeto:
1. [COMECE_AQUI.md](COMECE_AQUI.md) - Começo rápido
2. [README.md](README.md) - Documentação completa
3. [EXEMPLOS.md](EXEMPLOS.md) - Exemplos práticos

### 👨‍💻 Se você quer **entender** o código:
1. [RESUMO_PROJETO.md](RESUMO_PROJETO.md) - Visão geral
2. [DOCS_TECNICA.md](DOCS_TECNICA.md) - Arquitetura
3. [field_parser.py](field_parser.py) - Comece por aqui
4. [main.py](main.py) - Depois veja a orquestração

### 🧪 Se você quer **testar**:
1. [tests/README.md](tests/README.md) - Guia de testes
2. [tests/test_field_parser.py](tests/test_field_parser.py) - Testes principais
3. [tests/test_integration.py](tests/test_integration.py) - Testes de fluxo

### 🤝 Se você quer **contribuir**:
1. [CONTRIBUTING.md](CONTRIBUTING.md) - Guia de contribuição
2. [DOCS_TECNICA.md](DOCS_TECNICA.md) - Entender a arquitetura
3. [tests/](tests/) - Adicione testes para suas mudanças

## 🚀 Próximos Passos

1. Leia [COMECE_AQUI.md](COMECE_AQUI.md)
2. Execute: `python main.py --entrada ./pdfs --saida ./resultado --formato ambos`
3. Consulte [README.md](README.md) para opções avançadas
4. Explore [EXEMPLOS.md](EXEMPLOS.md) para mais casos de uso

---

**Projeto versão 1.0.0**  
Última atualização: 2024-01-15

