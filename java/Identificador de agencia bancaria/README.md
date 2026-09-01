# Identificador de Agência

Aplicação web completa para processamento e cruzamento de arquivos de dados posicionais, permitindo validação de agências bancárias através de NIBs.

## 🎯 Objetivo

Permite o upload de múltiplos arquivos de texto (`.txt`) em formato posicional/largura fixa e busca de códigos NIB (10 dígitos) com extração de sequências correspondentes (4 dígitos), exibindo resultados em tabela comparativa dinâmica.

## 🛠️ Stack Tecnológica

- **Backend:** Java 21 + Spring Boot 3.3.5 (Maven)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Execução:** 100% local (localhost:8080 para API, localhost:5173 para interface)

## 📋 Especificações Técnicas

### Posições de Extração (índices base 0)
- **NIB:** colunas 10-20 (10 dígitos)
- **Sequência:** colunas 48-52 (4 dígitos)
- **Tratamento:** linhas com menos de 52 caracteres são ignoradas com segurança

### Endpoints

```
POST /api/processar
```

Aceita `multipart/form-data`:
- `files`: Lista de arquivos `.txt`
- `nibs`: String com NIBs separados por espaço, vírgula ou quebra de linha

Retorna JSON com estrutura de resultados cruzados.

## 🚀 Como Executar

### Pré-requisitos

- **Java 21+** instalado e em PATH (ou configure `JAVA_HOME`)
- **Maven** instalado e em PATH (ou use o local em `.tools/`)
- **Node.js 18+** e npm para o frontend

### Inicialização Rápida

**Linux/macOS:**
```bash
./scripts/iniciar-projeto.sh
```

**Windows:**
```bash
scripts\iniciar-projeto.bat
```

O script automaticamente:
1. Detecta/instala dependências (Java, Maven, Node.js)
2. Inicia o backend na porta 8080
3. Inicia o frontend na porta 5173
4. Exibe URLs de acesso

### Inicialização Manual

**Backend:**
```bash
cd backend
mvn clean package -DskipTests
java -jar target/identificador-agencia-0.0.1-SNAPSHOT.jar
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Estrutura do Projeto

```
├── README.md                    # Este arquivo
├── .gitignore                  # Padrões de exclusão Git
├── docs/                       # Documentação
│   ├── Prompt.md              # Especificação funcional original
│   └── Redesign.md            # Guia de design UI/UX
├── scripts/                    # Scripts de inicialização
│   ├── iniciar-projeto.sh     # Linux/macOS
│   └── iniciar-projeto.bat    # Windows
├── backend/                    # Java Spring Boot
│   └── pom.xml                # Dependências Maven
└── frontend/                   # React + Vite + Tailwind
    ├── package.json           # Dependências npm
    ├── src/
    │   ├── App.tsx            # Aplicação principal
    │   ├── main.tsx           # Entry point
    │   └── index.css          # Estilos globais
    └── vite.config.ts         # Configuração Vite
```

## 🎨 Interface

- Upload drag-and-drop de múltiplos arquivos `.txt`
- Input de NIBs (suporta múltiplos formatos de separação)
- Tabela dinâmica com resultados cruzados
- Indicadores de status (Match, Discrepância, Erro)
- Filtro de busca rápida por NIB
- Exportação para CSV
- Design responsivo com Tailwind CSS

## 🔧 Desenvolvimento

### Build Frontend
```bash
cd frontend
npm install           # Instalar dependências
npm run dev          # Dev server com HMR
npm run build        # Build otimizado
npm run preview      # Preview de produção
```

### Build Backend
```bash
cd backend
mvn clean install    # Compilar e testes
mvn clean package -DskipTests  # Apenas compilar
mvn spring-boot:run  # Executar diretamente
```

## 📦 Dependências Principais

**Frontend:**
- React 18
- TypeScript 5.7
- Tailwind CSS 3.4
- Vite 6
- Lucide React (ícones)

**Backend:**
- Spring Boot 3.3.5
- Spring Web
- Spring Validation
- Java 21

## 💡 Funcionalidades

✅ Upload de múltiplos arquivos  
✅ Processamento em memória eficiente  
✅ Cruzamento de dados entre fontes  
✅ Filtro e busca rápida  
✅ Exportação CSV  
✅ Design responsivo  
✅ CORS habilitado para localhost:5173  
✅ Validação de entrada  
✅ Tratamento robusto de erros  

## 🤝 Contribuindo

Este é um projeto local. Mantenha a estrutura profissional, documente mudanças significativas e execute testes antes de commits.

## 📝 Licença

Uso privado. Todos os direitos reservados.

---

**Última atualização:** Setembro 2026
