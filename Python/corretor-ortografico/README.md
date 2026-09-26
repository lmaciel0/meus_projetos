# Corretor de Textos

Sistema local e gratuito de revisão de textos de ficção em português do Brasil, usando LanguageTool, Streamlit e SQLite. Funciona offline e não usa nenhuma API paga.

- **Aplicado automaticamente:** ortografia, acentuação, pontuação, crase e maiúsculas.
- **Sugestão com checkbox:** concordância verbal e nominal. O LanguageTool erra com mais frequência nesses casos, então cada uma só entra no texto se você marcar. A escolha fica salva no histórico.
- **Só observação:** sugestões de estilo (coloquialismos, abreviações, repetições) nunca são aplicadas, para preservar a voz do autor.

## Dicionário pessoal

O LanguageTool não aprende com exemplos, então os ajustes ficam no próprio corretor (salvos no `historico.db`), na aba **Dicionário**:

- **Palavras aceitas:** nunca são corrigidas nem aparecem nas observações. Servem para nomes de personagens, lugares, gírias e termos da história. Também dá para adicionar direto do resultado, em "Alguma dessas palavras está certa?"; a correção é desfeita no texto na hora.
- **Correções fixas:** "sempre `tava` → `estava`". Valem só para palavras inteiras, mesmo quando o LanguageTool não marca nada, e têm prioridade sobre as sugestões dele.

## Entrada por PDF

Além de colar o texto, dá para enviar um arquivo `.pdf`. O texto é extraído, os parágrafos são refeitos (juntando linhas quebradas e palavras hifenizadas no fim da linha, removendo números de página e separando as falas com travessão) e a correção segue o mesmo fluxo. O resultado aparece na tela e pode ser baixado como `.txt`; a formatação original do PDF não é preservada.

PDFs escaneados (imagem) não têm texto extraível e precisam passar por OCR antes. PDFs protegidos por senha também não são aceitos.

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

- `app.py` – interface Streamlit (abas Corrigir, Histórico e Dicionário)
- `corretor.py` – verificação com LanguageTool e aplicação das correções
- `pdf.py` – extração e normalização do texto de arquivos PDF
- `db.py` – histórico em SQLite (`historico.db`, criado automaticamente)
- `tests/` – testes (`pip install -r requirements-dev.txt` e depois `pytest`)
