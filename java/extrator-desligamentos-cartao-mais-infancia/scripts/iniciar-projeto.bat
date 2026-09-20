@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0.."
set "PROJ_ROOT=%CD%"

:: 1. Localizar Java
where java >nul 2>&1
if errorlevel 1 (
    if defined JAVA_HOME (
        set "CLEAN_JAVA_HOME=%JAVA_HOME%"
        if "!CLEAN_JAVA_HOME:~-1!"=="\" set "CLEAN_JAVA_HOME=!CLEAN_JAVA_HOME:~0,-1!"
        if exist "!CLEAN_JAVA_HOME!\bin\java.exe" set "PATH=!CLEAN_JAVA_HOME!\bin;!PATH!"
    )
)
where java >nul 2>&1
if errorlevel 1 (
    for /d %%J in ("C:\Program Files\Microsoft\jdk-*" "%LOCALAPPDATA%\Programs\Eclipse Adoptium\jdk-*" "C:\Program Files\Eclipse Adoptium\jdk-*" "C:\Program Files\Java\jdk-*") do (
        if exist "%%J\bin\java.exe" (
            set "JAVA_HOME=%%J"
            set "PATH=%%J\bin;!PATH!"
        )
    )
)
where java >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Java 21 ou superior nao foi encontrado.
    echo Instale o JDK e certifique-se de configurar o PATH ou JAVA_HOME.
    pause
    exit /b 1
)

:: 2. Localizar Maven ou Maven Wrapper
set "MVN_CMD="
where mvn >nul 2>&1
if not errorlevel 1 (
    set "MVN_CMD=mvn"
) else if exist "%PROJ_ROOT%\backend\mvnw.cmd" (
    set "MVN_CMD=call .\mvnw.cmd"
) else if exist "%USERPROFILE%\Downloads\apache-maven-3.9.16\bin\mvn.cmd" (
    set "MVN_CMD="%USERPROFILE%\Downloads\apache-maven-3.9.16\bin\mvn.cmd""
)

if not defined MVN_CMD (
    echo [ERRO] Maven nao encontrado e mvnw.cmd nao disponivel.
    pause
    exit /b 1
)

:: 3. Iniciar Backend
start "Extrator Desligamentos - Backend" cmd /k "cd /d "%PROJ_ROOT%\backend" && (if not exist "target\extrator-desligamentos-1.0.0.jar" %MVN_CMD% -q -DskipTests package) && java -jar target\extrator-desligamentos-1.0.0.jar"

:: 4. Iniciar Frontend
start "Extrator Desligamentos - Frontend" cmd /k "cd /d "%PROJ_ROOT%\frontend" && (if not exist "node_modules" call npm install) && npm run dev"

echo ==========================================================
echo  Extrator de Desligamentos (Java + React) iniciado!
echo  Backend:  http://localhost:8080
echo  Frontend: http://localhost:5173
echo ==========================================================
endlocal
