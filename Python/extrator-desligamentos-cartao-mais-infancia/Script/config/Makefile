.PHONY: help install test lint format run clean docker-build docker-run

# Variáveis
PYTHON := python3
PIP := pip3
PROJECT := leitor_desligamentos_cmic
VENV := venv

help:
	@echo "Comandos disponíveis:"
	@echo "  make install     - Instalar dependências"
	@echo "  make test        - Rodar testes"
	@echo "  make lint        - Verificar estilo de código"
	@echo "  make format      - Formatar código"
	@echo "  make run         - Executar script"
	@echo "  make clean       - Limpar arquivos temporários"
	@echo "  make docker-build - Construir imagem Docker"
	@echo "  make docker-run   - Rodar em Docker"
	@echo "  make help        - Mostrar esta ajuda"

install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest black flake8 isort pytest-cov

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

lint:
	flake8 . --exclude=$(VENV) --max-line-length=88 --count --statistics

format:
	black .
	isort .

run:
	$(PYTHON) main.py --entrada ./pdfs --saida ./resultado --formato ambos

run-xlsx:
	$(PYTHON) main.py --entrada ./pdfs --saida ./resultado --formato xlsx

run-csv:
	$(PYTHON) main.py --entrada ./pdfs --saida ./resultado --formato csv

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov *.egg-info dist build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete

docker-build:
	docker build -t $(PROJECT):latest .

docker-run:
	docker-compose up

docker-clean:
	docker-compose down
	docker rmi $(PROJECT):latest

check: lint test

# Targets de desenvolvimento
dev-setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	@echo "Virtual environment criado em $(VENV)/"
	@echo "Execute: source $(VENV)/bin/activate"

docs:
	@echo "Documentação disponível em:"
	@echo "  README.md          - Instruções de uso"
	@echo "  EXEMPLOS.md        - Exemplos de código"
	@echo "  DOCS_TECNICA.md    - Documentação técnica"
	@echo "  CONTRIBUTING.md    - Guia de contribuição"

version:
	@grep "__version__" main.py || echo "Versão não definida"

.DEFAULT_GOAL := help
