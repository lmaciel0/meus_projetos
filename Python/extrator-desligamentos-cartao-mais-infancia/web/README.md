# Leitor de Desligamentos Web

Aplicação local em Streamlit para extrair, revisar e exportar dados de formulários PDF de desligamento do Cartão Mais Infância Ceará.

## Funcionalidades

- Upload de vários PDFs e processamento de todas as páginas.
- Extração nativa com `pdfplumber` e fallback de OCR com `pytesseract`/`pdf2image`.
- Colunas `Arquivo`, `Referencia`, `MUNICIPIO`, `CPF`, `NIS`, `NOME` e `MOTIVO` em tabela editável.
- Data de referência preenchida com o dia do processamento e botão para limpar a seleção e os resultados.
- CPF e NIS preservados como texto, incluindo zeros à esquerda.
- Status automático `OK` ou `REVISAR`, exibido com indicadores verde/vermelho, e lista de inconsistências por arquivo.
- Filtros por município, motivo e status.
- Download em XLSX, CSV UTF-8 separado por ponto e vírgula e XLSX apenas dos registros `REVISAR`.
- Sem banco de dados: os arquivos são gravados apenas em diretórios temporários durante o processamento e removidos ao final.

## Requisitos

- Python 3.12 ou superior.
- Para OCR em Windows, instale também o Tesseract OCR e o Poppler. PDFs com texto selecionável não precisam desses programas.

## Execução local

No diretório `web`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Depois, abra o endereço local mostrado pelo Streamlit, normalmente `http://localhost:8501`.

## Testes

```powershell
python -m pytest -q
```

## Observações

O aplicativo não inventa valores ausentes. Um CPF com menos de 11 dígitos, ou qualquer campo obrigatório não identificado, marca o registro como `REVISAR` para correção manual.