# 🚀 COMECE AQUI - Guia Rápido de Início

Bem-vindo ao **Leitor de Desligamentos CMIC**!

Este arquivo fornece um guia passo-a-passo para começar a usar o projeto em 5 minutos.

## 📋 Pré-requisitos

- Python 3.12 ou superior
- pip (gerenciador de pacotes Python)
- (Opcional) Tesseract OCR para ler PDFs escaneados

## ⏱️ Instalação em 5 Minutos

### 1️⃣ Instalar Dependências (1 minuto)

**Windows:**
```bash
pip install -r requirements.txt
```

**macOS (com Homebrew):**
```bash
pip install -r requirements.txt
brew install tesseract  # Para OCR (opcional)
```

**Linux (Debian/Ubuntu):**
```bash
pip install -r requirements.txt
sudo apt-get install tesseract-ocr  # Para OCR (opcional)
```

### 2️⃣ Preparar Pasta de PDFs (1 minuto)

```bash
# Criar pasta
mkdir pdfs

# Colocar seus PDFs de desligamento aqui
# Copie os arquivos .pdf para a pasta 'pdfs/'
```

### 3️⃣ Executar o Script (1 minuto)

```bash
python main.py --entrada ./pdfs --saida ./resultado --formato ambos
```

### 4️⃣ Ver Resultados (1 minuto)

```bash
# A pasta 'resultado/' terá:
# - resultado_20240115_143022.xlsx
# - resultado_20240115_143022.csv
```

### 5️⃣ Abrir Resultados (1 minuto)

- Abra os arquivos XLSX/CSV com Excel, LibreOffice ou qualquer editor de planilhas
- Verifique os dados extraídos

## 💡 Exemplos Rápidos

### Apenas XLSX
```bash
python main.py --entrada ./pdfs --saida ./resultado --formato xlsx
```

### Apenas CSV
```bash
python main.py --entrada ./pdfs --saida ./resultado --formato csv
```

### Pastas aninhadas
```bash
python main.py --entrada ./documentos/pdfs --saida ./documentos/resultado
```

### Sem OCR (mais rápido)
```bash
python main.py --entrada ./pdfs --saida ./resultado --formato ambos --sem-ocr
```

## 🧪 Verificar se Tudo Funciona

```bash
# Executar testes
pytest tests/ -v

# Se passar, está tudo OK! ✅
```

## 📚 Próximos Passos

1. **Leia README.md**: Instruções completas
2. **Veja EXEMPLOS.md**: Mais casos de uso
3. **Consulte DOCS_TECNICA.md**: Para entender a arquitetura

## ⚠️ Troubleshooting

### "ModuleNotFoundError: No module named 'pdfplumber'"
```bash
# Solução: Instale as dependências
pip install -r requirements.txt
```

### "No such file or directory: './pdfs'"
```bash
# Solução: Crie a pasta de entrada
mkdir pdfs
# E coloque seus PDFs lá
```

### "tesseract is not installed" (apenas ao usar OCR)
```bash
# Windows (com Chocolatey)
choco install tesseract

# macOS
brew install tesseract

# Linux (Debian/Ubuntu)
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

### Resultados vazio ou incompleto
- Verifique se os PDFs têm o formato esperado
- Verifique se os campos estão nos padrões
- Consulte DOCS_TECNICA.md para padrões de regex

## 📞 Precisa de Ajuda?

- 📖 **Documentação**: Veja [README.md](README.md)
- 💬 **Exemplos**: Veja [EXEMPLOS.md](EXEMPLOS.md)
- 🔧 **Técnico**: Veja [DOCS_TECNICA.md](DOCS_TECNICA.md)
- 🤝 **Contribuições**: Veja [CONTRIBUTING.md](CONTRIBUTING.md)

## 🎯 O Que Você Consegue Fazer

✅ Extrair dados de múltiplos PDFs automaticamente  
✅ Exportar em Excel (XLSX) formatado profissionalmente  
✅ Exportar em CSV para análise  
✅ Processar PDFs com texto nativo  
✅ Processar PDFs escaneados (com OCR)  
✅ Marcar dados incompletos para revisão  
✅ Usar via CLI ou Python code  

## 📊 Campos Extraídos

O script extrai automaticamente:

1. **MUNICIPIO**: Município do beneficiário
2. **CPF**: CPF com 11 dígitos (preserva zeros à esquerda)
3. **NIS**: NIS com os dígitos (preserva zeros à esquerda)
4. **NOME**: Nome completo do responsável
5. **MOTIVO**: Motivo do desligamento (com descrição se OUTRO)

Além disso, adiciona:
- **ARQUIVO_ORIGEM**: Nome do PDF processado
- **STATUS_EXTRACAO**: OK ou REVISAR

## 🎓 Exemplos de Dados

Após executar, você terá resultados como:

| MUNICIPIO | CPF | NIS | NOME | MOTIVO | STATUS_EXTRACAO |
|-----------|-----|-----|------|--------|-----------------|
| FORTALEZA | 12345678900 | 12345678901 | JOÃO SILVA | Mudança para outro Estado | OK |
| MARACANAÚ | 09876543210 | 09876543211 | MARIA OLIVEIRA | OUTRO: Mudança de endereço | OK |
| CAUCAIA | 00123456789 | 00198765432 | PEDRO COSTA | Transferência de guarda | REVISAR |

---

**Pronto para começar? Execute:**
```bash
python main.py --entrada ./pdfs --saida ./resultado --formato ambos
```

🎉 **Boa sorte!**

