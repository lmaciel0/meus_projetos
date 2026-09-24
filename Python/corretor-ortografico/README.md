# Corretor de Textos

Sistema local de revisão de textos de ficção em português do Brasil, usando Claude (Anthropic API), Streamlit e SQLite.

Corrige ortografia, acentuação, pontuação, crase e concordância, sem mexer no estilo e na voz do autor.

## Como rodar

1. Copie `.env.example` para `.env` e preencha `ANTHROPIC_API_KEY`.
2. Dê um clique duplo em `iniciar.bat`. Na primeira vez ele cria o `.venv` e instala as dependências.

Ou, manualmente:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app.py
```

## Estrutura

- `app.py` – interface Streamlit (abas Corrigir e Histórico)
- `corretor.py` – chamada à API da Anthropic
- `prompts.py` – system prompt e schema JSON da resposta
- `db.py` – histórico em SQLite (`historico.db`, criado automaticamente)
