#!/bin/bash
# Script de ajuda para o Leitor de Desligamentos CMIC
# Use este script para executar tarefas comuns

set -e

show_help() {
    cat << EOF

Leitor de Desligamentos CMIC - Script de Ajuda
===============================================

Uso: ./help.sh COMANDO [argumentos]

Comandos disponíveis:
  help             - Mostra esta mensagem
  install          - Instala dependências do projeto
  test             - Executa testes unitários
  run              - Executa o processamento (uso: ./help.sh run <entrada> <saida> [formato])
  lint             - Executa verificação de lint (flake8)
  format           - Formata código (black + isort)
  clean            - Remove arquivos temporários e cache

Exemplos:
  ./help.sh install
  ./help.sh test
  ./help.sh run ./pdfs ./resultado
  ./help.sh run ./pdfs ./resultado xlsx

EOF
}

install() {
    echo "Instalando dependências..."
    pip install -r requirements.txt
    echo "✓ Dependências instaladas com sucesso!"
}

test() {
    echo "Executando testes unitários..."
    pytest tests/ -v
    echo "✓ Testes executados com sucesso!"
}

run() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "ERRO: Digite os argumentos necessários"
        echo "Uso: ./help.sh run <pasta_entrada> <pasta_saida> [formato]"
        exit 1
    fi

    ENTRADA="$1"
    SAIDA="$2"
    FORMATO="${3:-ambos}"

    echo ""
    echo "Processando PDFs..."
    echo "Entrada: $ENTRADA"
    echo "Saída: $SAIDA"
    echo "Formato: $FORMATO"
    echo ""

    python main.py --entrada "$ENTRADA" --saida "$SAIDA" --formato "$FORMATO"
    echo "✓ Processamento concluído com sucesso!"
}

lint() {
    echo "Executando lint (flake8)..."
    flake8 . --exclude=venv,__pycache__,.git
    echo "✓ Lint passou com sucesso!"
}

format() {
    echo "Formatando código (black)..."
    black . --exclude=venv,__pycache__,.git

    echo "Organizando imports (isort)..."
    isort . --skip=venv,__pycache__,.git

    echo "✓ Formatação concluída!"
}

clean() {
    echo "Limpando arquivos temporários..."
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
    echo "✓ Limpeza concluída!"
}

# Main
case "${1:-help}" in
    help)
        show_help
        ;;
    install)
        install
        ;;
    test)
        test
        ;;
    run)
        shift
        run "$@"
        ;;
    lint)
        lint
        ;;
    format)
        format
        ;;
    clean)
        clean
        ;;
    *)
        echo "Comando desconhecido: $1"
        show_help
        exit 1
        ;;
esac
