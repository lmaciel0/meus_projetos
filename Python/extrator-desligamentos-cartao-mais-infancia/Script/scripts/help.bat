@echo off
REM Script de ajuda para o Leitor de Desligamentos CMIC
REM Use este script para executar tarefas comuns

setlocal enabledelayedexpansion

if "%1"=="" (
    goto :show_help
)

if /i "%1"=="help" (
    goto :show_help
)

if /i "%1"=="install" (
    goto :install
)

if /i "%1"=="test" (
    goto :test
)

if /i "%1"=="run" (
    goto :run
)

if /i "%1"=="lint" (
    goto :lint
)

if /i "%1"=="format" (
    goto :format
)

echo Comando desconhecido: %1
goto :show_help

:show_help
echo.
echo Leitor de Desligamentos CMIC - Script de Ajuda
echo ===============================================
echo.
echo Uso: help.bat COMANDO [argumentos]
echo.
echo Comandos disponíveis:
echo   help             - Mostra esta mensagem
echo   install          - Instala dependências do projeto
echo   test             - Executa testes unitários
echo   run              - Executa o processamento (uso: help.bat run ^<entrada^> ^<saida^> [formato])
echo   lint             - Executa verificação de lint (flake8)
echo   format           - Formata código (black + isort)
echo.
echo Exemplos:
echo   help.bat install
echo   help.bat test
echo   help.bat run ./pdfs ./resultado
echo   help.bat run ./pdfs ./resultado xlsx
echo.
goto :end

:install
echo Instalando dependências...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO ao instalar dependências!
    goto :end
)
echo Dependências instaladas com sucesso!
goto :end

:test
echo Executando testes unitários...
pytest tests/ -v
if errorlevel 1 (
    echo ERRO ao executar testes!
    goto :end
)
echo Testes executados com sucesso!
goto :end

:run
if "%2"=="" (
    echo ERRO: Digite os argumentos necessários
    echo Uso: help.bat run ^<pasta_entrada^> ^<pasta_saida^> [formato]
    goto :end
)

set ENTRADA=%2
set SAIDA=%3
set FORMATO=%4

if "%FORMATO%"=="" (
    set FORMATO=ambos
)

echo.
echo Processando PDFs...
echo Entrada: !ENTRADA!
echo Saída: !SAIDA!
echo Formato: !FORMATO!
echo.

python main.py --entrada !ENTRADA! --saida !SAIDA! --formato !FORMATO!

if errorlevel 1 (
    echo ERRO ao processar PDFs!
    goto :end
)

echo Processamento concluído com sucesso!
goto :end

:lint
echo Executando lint (flake8)...
flake8 . --exclude=venv,__pycache__,.git
if errorlevel 1 (
    echo Lint encontrou problemas!
    goto :end
)
echo Lint passou com sucesso!
goto :end

:format
echo Formatando código (black)...
black . --exclude=venv,__pycache__,.git

echo Organizando imports (isort)...
isort . --skip=venv,__pycache__,.git

echo Formatação concluída!
goto :end

:end
echo.
