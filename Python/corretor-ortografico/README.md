# Corretor de Textos

Sistema local e gratuito de revisão de textos de ficção em português do Brasil, usando LanguageTool (ou uma IA local, opcional), Streamlit e SQLite. Funciona offline e não usa nenhuma API paga.

## Revisão com IA local (opcional)

Na aba Corrigir, em **Revisar com**, dá para trocar o LanguageTool por uma IA que roda no próprio computador: o Gemma 4 E4B, pelo [Ollama](https://ollama.com). Ela entende o contexto e pega muito mais erros de digitação: num teste com dois trechos de ficção digitados às pressas, corrigiu 43 de 55 erros, contra 17 do LanguageTool.

- **Tudo o que a IA muda vira sugestão com checkbox**, com um trecho da frase em volta. Nada entra no texto sozinho, porque às vezes ela muda o sentido ("ele e a Kessa" → "ele é a Kessa"). Use **Aceitar todas** / **Recusar todas** para decidir de uma vez e desmarque o que estiver errado.
- **Continuam valendo** o dicionário pessoal (a IA recebe os nomes e não pode trocá-los), as correções fixas, os travessões e as repetições. Marcas de oralidade ("pra", "tá") não são trocadas pela forma formal.
- **É lenta sem placa de vídeo:** cerca de 1 minuto a cada 75 palavras num notebook comum, então um capítulo de 3.000 palavras leva uns 40 minutos. O texto vai em blocos de parágrafos, com barra de progresso e estimativa do tempo restante. Os parágrafos revisados ficam guardados no `historico.db`: se a revisão for interrompida, a próxima continua de onde parou.

Para usar: instale o [Ollama](https://ollama.com/download) e baixe o modelo (6,1 GB) no terminal:

```bash
ollama pull gemma4:e4b-it-qat
```

O Ollama precisa estar aberto (ele fica na bandeja do Windows). Para usar outro modelo ou um Ollama em outra máquina, defina as variáveis de ambiente `CORRETOR_MODELO_IA` e `CORRETOR_OLLAMA_URL`. Modelos com final `:cloud` rodam fora do computador e não são recomendados.

- **Aplicado automaticamente:** ortografia, acentuação, pontuação, crase e maiúsculas. Palavras grudadas ("noslençois") são separadas e corrigidas ("nos lençóis").
- **Sugestão com checkbox:** concordância verbal e nominal, e correções de ortografia muito diferentes da palavra original (mais de 2 letras, sem contar acentos). O LanguageTool erra com mais frequência nesses casos, então cada uma só entra no texto se você marcar. A escolha fica salva no histórico. Quando não dá para saber se a palavra tem um erro de digitação ou está grudada na seguinte ("decasa": "década" ou "de casa"?), você escolhe entre as opções.
- **Só observação:** sugestões de estilo (coloquialismos, abreviações, repetições) nunca são aplicadas, para preservar a voz do autor.
- **Travessões:** falas marcadas com hífen (`- Vem? -- perguntou ele.`) ganham travessão (`— Vem? — perguntou ele.`).

## Revisando o resultado

- **Correções aplicadas:** cada uma tem um checkbox em **Aplicar**. Desmarque para desfazer só naquele texto; para nunca mais corrigir a palavra, use "Alguma dessas palavras está certa sempre?".
- **Alterações destacadas:** o texto corrigido com o que saiu riscado e o que entrou em verde, além da visão lado a lado.
- **Edição manual:** o texto corrigido pode ser editado direto no campo e salvo com **Salvar edição**. Enquanto houver edição salva, as correções ficam travadas (mudá-las apagaria a edição); **Descartar edição** volta ao texto das correções.
- **Observações:** além do estilo, apontam palavras repetidas em pouco espaço e nomes escritos de jeitos diferentes ("Aelyn" num texto em que o nome é "Aelin"). Cada uma pode ser **aplicada** (quando há sugestão), **dispensada** ou **silenciada**: silenciar esconde aquele tipo de aviso nas próximas correções; dá para reativar na aba Dicionário.
- **Estatísticas:** palavras, parágrafos e as palavras que você mais usou.
- **Textos longos** vão ao LanguageTool em partes, com barra de progresso. Parágrafos já verificados são reaproveitados enquanto o app estiver aberto, então corrigir de novo um texto com poucas mudanças é rápido.

## Dicionário pessoal

O LanguageTool não aprende com exemplos, então os ajustes ficam no próprio corretor (salvos no `historico.db`), na aba **Dicionário**:

- **Palavras aceitas:** nunca são corrigidas nem aparecem nas observações. Servem para nomes de personagens, lugares, gírias e termos da história. Também dá para adicionar direto do resultado, em "Alguma dessas palavras está certa?"; a correção é desfeita no texto na hora.
- **Correções fixas:** "sempre `tava` → `estava`". Valem só para palavras inteiras, mesmo quando o LanguageTool não marca nada, e têm prioridade sobre as sugestões dele. Maiúsculas são respeitadas ("Tava" → "Estava", "TAVA" → "ESTAVA").
- **Sugeridas pelo seu histórico:** correções que você aceitou 3 vezes ou mais aparecem com um botão **Tornar fixa**.
- **Avisos silenciados:** os tipos de observação que você silenciou, com o botão **Reativar**.

## Backup

Na aba **Backup** dá para baixar um `.json` com o dicionário pessoal, os avisos silenciados e o histórico, e restaurá-lo em outro computador. A restauração junta ao que já existe, sem apagar nada nem duplicar textos. Os arquivos `.docx` enviados não entram no backup, só os textos.

## Entrada por Word e PDF

Além de colar o texto, dá para enviar um arquivo:

- **Word (`.docx`):** cada parágrafo do documento é corrigido e o resultado pode ser baixado em `.docx` **com a formatação original** (itálicos, negritos, estilos). Tabelas, cabeçalhos, rodapés e notas não são corrigidos. Se a edição manual mudar o número de parágrafos, o `.docx` baixado é um documento simples.
- **PDF:** o texto é extraído e os parágrafos são refeitos (juntando linhas quebradas e palavras hifenizadas no fim da linha, removendo números de página e separando as falas com travessão). A formatação do PDF não é preservada. PDFs protegidos por senha não são aceitos.

Qualquer resultado pode ser baixado como `.txt` ou `.docx`.

### PDFs escaneados (OCR, opcional)

PDFs escaneados (imagem) não têm texto. Se o [OCRmyPDF](https://ocrmypdf.readthedocs.io/) estiver instalado, com o Tesseract e o idioma português (`por`), o corretor o usa sozinho para reconhecer o texto; sem ele, o PDF precisa passar por OCR antes.

## Requisitos

- Python 3.10+
- Java 17+ (o LanguageTool roda localmente em Java)
- Opcional: [Ollama](https://ollama.com) com o modelo `gemma4:e4b-it-qat`, para a revisão com IA (16 GB de RAM recomendados)

## Como rodar

Dê um clique duplo em `iniciar.bat`. Na primeira vez ele cria o `.venv` e instala as dependências. A primeira correção baixa o LanguageTool (~260 MB, só uma vez) e leva cerca de 1 minuto para iniciar.

Ou, manualmente:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app.py
```

## Estrutura

- `app.py` – interface Streamlit (abas Corrigir, Histórico, Dicionário e Backup)
- `corretor.py` – verificação com LanguageTool (em blocos, com cache) e aplicação das correções
- `ia.py` – revisão com IA local pelo Ollama, com as diferenças convertidas em sugestões
- `analise.py` – repetições, nomes com grafias diferentes e estatísticas
- `diferencas.py` – destaque das alterações
- `docx_io.py` – leitura e escrita de `.docx` preservando a formatação
- `pdf.py` – extração e normalização do texto de arquivos PDF, com OCR opcional
- `db.py` – histórico em SQLite (`historico.db`, criado automaticamente)
- `tests/` – testes, inclusive da interface (`pip install -r requirements-dev.txt` e depois `pytest`)
