# Use imagem Python 3.12 slim
FROM python:3.12-slim

# Definir label de metadados
LABEL maintainer="Prefeitura Municipal de Fortaleza"
LABEL description="Leitor de Desligamentos - Cartão Mais Infância Ceará"
LABEL version="1.0.0"

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (incluindo Tesseract para OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Criar diretórios de entrada e saída
RUN mkdir -p /app/input /app/output

# Volume para entrada de PDFs
VOLUME ["/app/input", "/app/output"]

# Comando padrão
ENTRYPOINT ["python", "main.py"]

# Argumentos padrão
CMD ["--entrada", "/app/input", "--saida", "/app/output", "--formato", "ambos"]
