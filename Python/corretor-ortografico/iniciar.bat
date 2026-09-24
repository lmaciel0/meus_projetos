@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    python -m venv .venv || (echo [ERRO] Python nao encontrado. & pause & exit /b 1)
    .venv\Scripts\python.exe -m pip install -r requirements.txt || (pause & exit /b 1)
)

if not exist ".env" (
    echo [AVISO] Arquivo .env nao encontrado. Copie .env.example para .env e informe sua ANTHROPIC_API_KEY.
    pause
    exit /b 1
)

.venv\Scripts\python.exe -m streamlit run app.py
