@echo off
setlocal
rem O script fica em scripts\; o projeto esta na pasta acima.
set "PROJECT_DIR=%~dp0..\"
set "JAVA_HOME=%LOCALAPPDATA%\Programs\Eclipse Adoptium\jdk-25.0.4.101-hotspot"
if not exist "%JAVA_HOME%\bin\java.exe" (
	echo ERRO: JDK nao encontrado em "%JAVA_HOME%".
	echo Instale um JDK 17 ou superior e atualize JAVA_HOME neste arquivo.
	pause
	exit /b 1
)
set "MAVEN_HOME=%PROJECT_DIR%.tools\apache-maven-3.9.10"
if not exist "%MAVEN_HOME%\bin\mvn.cmd" (
	echo ERRO: Maven local nao encontrado em "%MAVEN_HOME%".
	echo Execute a instalacao do Maven ou reinstale a estrutura do projeto.
	pause
	exit /b 1
)
set "PATH=%JAVA_HOME%\bin;%MAVEN_HOME%\bin;%PATH%"
start "Backend" cmd /k "cd /d %PROJECT_DIR%backend && mvn -q -DskipTests package && java -jar target\identificador-agencia.jar"
start "Frontend" cmd /k "cd /d %PROJECT_DIR%frontend && npm install && npm run dev"
echo Backend: http://localhost:8080
echo Frontend: http://localhost:5173
endlocal