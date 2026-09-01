
Você é um desenvolvedor full-stack sênior especialista em Java e React. 

Crie uma aplicação web completa projetada para rodar exclusivamente em ambiente local (localhost) com backend em Java (Spring Boot) e frontend em React (com Vite e Tailwind CSS).

### 🎯 Objetivo do Sistema
A aplicação deve permitir o processamento e cruzamento de múltiplos arquivos de texto (`.txt`) posicionais/de largura fixa. O usuário fará o upload de múltiplos arquivos `.txt` e informará uma lista de códigos "NIB". O sistema deve buscar cada NIB linha por linha em cada arquivo e extrair uma sequência de 4 dígitos correspondente, exibindo os resultados em uma tabela comparativa dinâmica.+

---

### 📐 Regras de Extração e Posição (Layout Posicional)
Considere índices de coluna base 1 (coluna 1 = primeiro caractere da linha):
1. **NIB (Identificador):**
   - Localizado da **coluna 11 até a coluna 20** (10 dígitos).
   - Em Java/JavaScript (base 0): `linha.substring(10, 20).trim()`.
2. **Sequência Alvo (4 Dígitos):**
   - Localizada da **coluna 49 até a coluna 52** (4 dígitos).
   - Em Java/JavaScript (base 0): `linha.substring(48, 52).trim()`.
3. **Tratamento de Linhas Curtas:**
   - Se uma linha tiver menos de 52 caracteres, ela deve ser ignorada com segurança sem gerar exceção de `IndexOutOfBounds`.

---

### 🛠️ Stack Tecnológica
- **Backend:** Java 17+ / 21 com Spring Boot 3 (Maven ou Gradle), Spring Web, CORS habilitado para `http://localhost:5173`.
- **Frontend:** React (Vite), TypeScript, Tailwind CSS (e Lucide-React para ícones).
- **Execução:** 100% local (`localhost:8080` para API e `localhost:5173` para frontend).

---

### 🖥️ Interface do Usuário (Frontend)
1. **Área de Upload:**
   - Campo para selecionar ou arrastar múltiplos arquivos `.txt`.
   - Lista visual com os nomes dos arquivos carregados e botão para remover arquivos individuais.
2. **Entrada de NIBs:**
   - Uma `textarea` espaçosa onde o usuário cola a lista de NIBs (aceitando múltiplos NIBs separados por quebra de linha, vírgula ou espaço).
   - Contador de quantos NIBs foram inseridos.
3. **Ações:**
   - Botão de "Processar / Pesquisar" com feedback visual de carregamento (spinner/progresso).
   - Botão de "Limpar Tudo".
4. **Tabela de Resultados:**
   - **Coluna 1:** `NIB Pesquisado`
   - **Colunas seguintes:** Uma coluna para cada arquivo carregado (com o nome do arquivo no cabeçalho).
   - **Células:** A sequência de 4 dígitos encontrada naquele arquivo para aquele NIB. Caso o NIB não exista no arquivo, exibir um traço `-` ou badge discreta `Não encontrado`.
   - **Funcionalidades extras na tabela:**
     - Botão para exportar o resultado para **Excel (.xlsx)** ou **CSV**.
     - Campo de busca rápida/filtro na tabela gerada.

---

### ⚙️ Arquitetura do Backend (Java Spring Boot)
1. **Endpoint REST:**
   - `POST /api/processar`
   - Aceita `multipart/form-data` contendo:
     - `files`: Lista de `MultipartFile` (`.txt`).
     - `nibs`: Lista de `String` (os NIBs a serem consultados).
2. **Processamento em Memória Eficiente:**
   - Ler os arquivos usando `BufferedReader` / streams para evitar alto consumo de memória.
   - Montar um mapa em memória: `Map<String, Map<String, String>>` onde a chave principal é o `NIB`, a chave secundária é o `NomeDoArquivo`, e o valor são os `4 Dígitos`.
3. **Retorno do Endpoint (JSON):**
   - Retornar a lista de nomes dos arquivos e a lista estruturada de linhas com os valores para cada NIB.

---

### 📦 Entregáveis Esperados
1. Estrutura completa de pastas do projeto.
2. Código fonte completo e funcional do backend Java (Controller, Service, DTOs e configuração CORS).
3. Código fonte completo do frontend React (componentes, estilos Tailwind e chamada à API com Axios/Fetch).
4. Instruções claras passo a passo de como rodar o backend e o frontend no terminal local.