# Prompt para Redesign do Identificador de Agência

Você é um designer de UI/UX especializado em interfaces web modernas e intuitivas. Preciso que você redesenhe completamente a interface da aplicação "Identificador de Agência" seguindo as diretrizes abaixo.

## 📋 Contexto da Aplicação

A aplicação "Identificador de Agência" é uma ferramenta que permite:
- Carregar múltiplos arquivos de dados (.txt)
- Inserir uma lista de NIBs para buscar
- Processar e cruzar dados entre fontes
- Exibir resultados com indicadores de status (match, discrepância, erro)

## 🎨 Especificações de Design

### 1. **Hierarquia Visual Clara**
- Título principal e subtítulo bem definidos
- Seções agrupadas em cards separados (não em um bloco único)
- Ícones visuais para cada seção (use Tabler icons)
- Rótulos com labels pequenos e em maiúsculas (12px, uppercase)

### 2. **Layout em Grade (Grid)**
- Estrutura responsiva com 2 colunas para "Arquivos" e "NIBs"
- Botões de ação (Processar / Limpar) centralizados abaixo das seções
- Resultado expandido na linha abaixo
- Bom uso de whitespace e espaçamento

### 3. **Paleta de Cores**
- **Azul claro**: use para elementos primários, headers, elementos de foco
  - Sugestão: `#E3F2FD` (background), `#1976D2` (primário)
- **Verde claro**: use para indicadores de sucesso, status positivos
  - Sugestão: `#E8F5E9` (background), `#388E3C` (primário)
- **Cinza neutro**: backgrounds e borders
  - Sugestão: `#F5F5F5` (surface), `#BDBDBD` (border)
- **Vermelho suave**: para erros e discrepâncias
  - Sugestão: `#FFEBEE` (background), `#D32F2F` (primário)
- **Amarelo suave**: para avisos/discrepâncias leves
  - Sugestão: `#FFF8E1` (background), `#F57F17` (primário)

### 4. **Tipografia com Fonte Arredondada**
- Usar fonte com características arredondadas e amigáveis
  - **Sugestão**: `font-family: 'Inter', 'Segoe UI', '-apple-system'` (com border-radius aplicado)
  - Ou alternativa: `'Poppins'`, `'Quicksand'`, `'Nunito'`
- H1 (Título): 28px, weight 500, azul primário
- H2 (Seções): 14px, weight 500, cinza escuro
- Body: 13px-14px, weight 400, cinza escuro
- Labels: 12px, weight 500, uppercase, cinza secundário
- Aplicar `border-radius: 12px` em cards e `8px` em inputs/buttons

### 5. **Componentes de Card**
- Background: branco ou cinza muito claro (`#FAFAFA`)
- Border: 0.5px sólido, cinza claro (`#E0E0E0`)
- Border-radius: 12px
- Padding: 1.25rem (20px)
- Sombra sutil (opcional): `box-shadow: 0 1px 3px rgba(0,0,0,0.08)`

### 6. **Seção "Arquivos de Origem"**
- Card com ícone de upload (ti-upload) à esquerda do título
- Mostrar quantidade de arquivos carregados
- Listar arquivos com visual de tags/pills (fundo azul claro, texto azul)
- Botão "+ Adicionar arquivos" com border simples

### 7. **Seção "NIBs para Buscar"**
- Card com ícone de lista (ti-list-check)
- Mostrar quantidade de NIBs
- Textarea/caixa de texto scrollável com NIBs listados
- Botão "Colar lista" com border simples

### 8. **Botões de Ação**
- **Botão Primário "Processar"**:
  - Background: azul primário (`#1976D2`)
  - Text: branco
  - Ícone: play (ti-player-play)
  - Hover: azul mais escuro
  - Padding: 10px 16px
  - Border-radius: 8px
  - Peso: 500

- **Botão Secundário "Limpar"**:
  - Background: transparente
  - Border: 1px sólido, cinza médio
  - Text: cinza escuro
  - Hover: background cinza claro
  - Mesmas dimensões do primário

### 9. **Tabela de Resultados**
- Header com background azul muito claro (`#E3F2FD`)
- Linhas alternadas com background branco e cinza muito claro (`#FAFAFA`)
- Border entre linhas: 0.5px, cinza claro
- NIB em destaque (font-weight: 500, azul)
- Valores: preto normal
- **Valores discrepantes em vermelho** para destacar inconsistências
- Última coluna: indicadores visuais (bolinhas coloridas)
  - Verde (`#388E3C`) = match
  - Amarelo (`#F57F17`) = discrepância
  - Vermelho (`#D32F2F`) = erro

### 10. **Indicadores de Status**
- Usar bolinhas coloridas (8px de diâmetro, border-radius: 50%)
- Verde: dados conferem/match
- Amarelo: valores diferentes detectados
- Vermelho: erro ou inconsistência crítica

### 11. **Botões Secundários (Footer da Tabela)**
- "Filtrar" com ícone (ti-search)
- "Exportar CSV" com ícone (ti-download)
- Background: transparente
- Border: 1px sólido, cinza
- Font-size: 12px
- Hover: background cinza claro

### 12. **Espaçamento e Layout**
- Gap entre colunas: 20px
- Margin bottom entre seções: 3rem (48px)
- Padding dentro de cards: 1.25rem (20px)
- Padding vertical geral: 2rem (32px)
- Max-width: 900px (centralizado)

### 13. **Texto e Microcópia**
- Usar sentence case (não ALL CAPS) em tudo
- "Processar" (não "PROCESSAR")
- "Identificador de agência" (não "IDENTIFICADOR DE AGÊNCIA")
- Labels pequenas em uppercase apenas (ex: "OPERAÇÃO LOCAL")
- Descrições claras: "Cruze dados de múltiplas fontes para validar agências"

### 14. **Responsividade**
- Em telas menores (< 768px):
  - Cards de arquivos/NIBs em 1 coluna
  - Tabela com scroll horizontal se necessário
  - Botões em full-width

## 🚀 Entregáveis

Implemente estas alterações em:
1. **HTML/CSS**: Estrutura semântica + estilos
2. **Tipografia**: Fonte arredondada consistente em todo projeto
3. **Componentes**: Cards, buttons, inputs com visual refinado
4. **Cores**: Azul claro, verde claro, com destaques em vermelho/amarelo
5. **Ícones**: Tabler icons integrados onde apropriado

## 📐 Resumo Visual de Mudanças

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Cards | Nenhum | Separação clara (12px radius, border, bg) |
| Ícones | Nenhum | Tabler para cada seção |
| Cores | Marrom/Laranja | Azul e verde claros |
| Fonte | Sans genérica | Arredondada (Inter/Poppins/Quicksand) |
| Status | Tabela plana | Indicadores visuais coloridos |
| Espaço | Apertado | Whitespace generoso (1.25rem+) |
| Botões | Genéricos | Clay-style primary + outline secondary |

## 🎯 Prioridades

1. **Implementar a paleta de cores** (azul claro, verde claro)
2. **Aplicar fonte arredondada** em todo o projeto
3. **Redesenhar cards** com borders, shadows e spacing
4. **Adicionar indicadores visuais** na tabela de resultados
5. **Refinar tipografia** com hierarquia clara
6. **Validar responsividade** em mobile

Comece pelo HTML structure, depois CSS styling. Use variáveis CSS para cores para facilitar futuras manutenções.
