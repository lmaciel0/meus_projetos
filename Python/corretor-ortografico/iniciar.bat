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
    .venv\Scripts\python.exe -m pip install -r requirements.txt || (pause & exit /b 1)
)

.venv\Scripts\python.exe -m streamlit run app.py
