# Corretor de Textos

Sistema local e gratuito de revisão de textos de ficção em português do Brasil, usando LanguageTool, Streamlit e SQLite. Funciona offline e não usa nenhuma API paga.

- **Aplicado automaticamente:** ortografia, acentuação, pontuação, crase e maiúsculas.
- **Sugestão com checkbox:** concordância verbal e nominal. O LanguageTool erra com mais frequência nesses casos, então cada uma só entra no texto se você marcar. A escolha fica salva no histórico.
- **Só observação:** sugestões de estilo (coloquialismos, abreviações, repetições) nunca são aplicadas, para preservar a voz do autor.

## Requisitos

- Python 3.10+
- Java 17+ (o LanguageTool roda localmente em Java)

## Como rodar

Dê um clique duplo em `iniciar.bat`. Na primeira vez ele cria o `.venv` e instala as dependências. A primeira correção baixa o LanguageTool (~260 MB, só uma vez) e leva cerca de 1 minuto para iniciar.

Ou, manualmente:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app.py
```

## Estrutura

- `app.py` – interface Streamlit (abas Corrigir e Histórico)
- `corretor.py` – verificação com LanguageTool e aplicação das correções
- `db.py` – histórico em SQLite (`historico.db`, criado automaticamente)
