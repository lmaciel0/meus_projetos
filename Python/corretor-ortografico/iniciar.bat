@echo off
cd /d "%~dp0"

where java >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Java nao encontrado. O LanguageTool precisa do Java 17 ou superior.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    python -m venv .venv || (echo [ERRO] Python nao encontrado. & pause & exit /b 1)
)

rem Fora do bloco acima: se uma instalacao anterior falhou no meio, tenta de novo.
.venv\Scripts\python.exe -c "import streamlit, language_tool_python" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    .venv\Scripts\python.exe -m pip install -r requirements.txt || (pause & exit /b 1)
)

.venv\Scripts\python.exe -m streamlit run app.py
