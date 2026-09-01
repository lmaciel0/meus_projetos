#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_LOG="$SCRIPT_DIR/backend.log"
FRONTEND_LOG="$SCRIPT_DIR/frontend.log"

if ! command -v java >/dev/null 2>&1; then
  if [ -n "${JAVA_HOME:-}" ] && [ -x "$JAVA_HOME/bin/java" ]; then
    export PATH="$JAVA_HOME/bin:$PATH"
  else
    for candidate in \
      "$HOME/.local/tools/jdk-17" \
      "$HOME/.local/tools/jdk-21" \
      /usr/lib/jvm/default-java \
      /usr/lib/jvm/java-17-openjdk-amd64 \
      /usr/lib/jvm/java-21-openjdk-amd64 \
      /usr/lib/jvm/java-17-openjdk \
      /usr/lib/jvm/java-21-openjdk \
      /usr/lib/jvm/*; do
      if [ -x "$candidate/bin/java" ]; then
        export JAVA_HOME="$candidate"
        export PATH="$JAVA_HOME/bin:$PATH"
        break
      fi
    done
  fi
fi

if ! command -v mvn >/dev/null 2>&1; then
  if [ -n "${MAVEN_HOME:-}" ] && [ -x "$MAVEN_HOME/bin/mvn" ]; then
    export PATH="$MAVEN_HOME/bin:$PATH"
  else
    for candidate in \
      "$HOME/.local/tools/apache-maven-3.9.10" \
      "$HOME/.local/tools/apache-maven-3.9.11" \
      /usr/share/maven \
      /opt/maven \
      /usr/local/apache-maven \
      /usr/local/maven \
      /snap/maven/current; do
      if [ -x "$candidate/bin/mvn" ]; then
        export MAVEN_HOME="$candidate"
        export PATH="$MAVEN_HOME/bin:$PATH"
        break
      fi
    done
  fi
fi

if ! command -v java >/dev/null 2>&1; then
  echo "ERRO: Java nao encontrado. Instale o JDK 17+ e tente novamente."
  echo "Exemplo: sudo apt install openjdk-17-jdk"
  exit 1
fi

if ! command -v mvn >/dev/null 2>&1; then
  echo "ERRO: Maven nao encontrado. Instale o Maven e tente novamente."
  echo "Exemplo: sudo apt install maven"
  exit 1
fi

if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
  echo "ERRO: Estrutura do projeto nao encontrada em $SCRIPT_DIR"
  exit 1
fi

if [ -f "$BACKEND_LOG" ]; then
  rm -f "$BACKEND_LOG"
fi

if [ -f "$FRONTEND_LOG" ]; then
  rm -f "$FRONTEND_LOG"
fi

nohup bash -lc "cd '$BACKEND_DIR' && mvn -q -DskipTests package && java -jar target/identificador-agencia-0.0.1-SNAPSHOT.jar" > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

nohup bash -lc "cd '$FRONTEND_DIR' && npm install && npm run dev -- --host 0.0.0.0 --port 5173" > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

sleep 8

echo "========================================"
echo "Projeto iniciado com sucesso!"
echo "Backend: http://localhost:8080"
echo "Frontend: http://localhost:5173"
echo "Processos em background:"
echo "  Backend PID: $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo "Logs:"
echo "  Backend: $BACKEND_LOG"
echo "  Frontend: $FRONTEND_LOG"
echo "========================================"
echo ""
echo "Para encerrar os serviços:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

if [ -f "$BACKEND_LOG" ]; then
  echo "[Backend] Status inicial:"
  tail -n 10 "$BACKEND_LOG"
fi

if [ -f "$FRONTEND_LOG" ]; then
  echo ""
  echo "[Frontend] Status inicial:"
  tail -n 15 "$FRONTEND_LOG"
fi
