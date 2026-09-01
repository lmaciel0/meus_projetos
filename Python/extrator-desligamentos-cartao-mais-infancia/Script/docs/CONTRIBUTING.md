# Contribuindo para o Leitor de Desligamentos CMIC

Obrigado por se interessar em contribuir com este projeto! Este documento fornece diretrizes e instruções para contribuir.

## 📋 Código de Conduta

Este projeto adota um Código de Conduta. Por favor, leia-o antes de participar.

- Seja respeitoso com todos os participantes
- Críticas devem ser construtivas
- Reporte comportamento abusivo

## 🐛 Reportando Bugs

Antes de relatar um bug, verifique se ele já foi reportado. Se você encontrar um novo bug:

1. **Use um título claro e descritivo**
2. **Forneça uma descrição detalhada** do problema
3. **Forneça exemplos específicos** para demonstrar os passos
4. **Descreva o comportamento observado** e o que você esperava
5. **Inclua screenshots ou logs** se aplicável
6. **Indique sua versão do Python** e do sistema operacional

### Formato de Reporte de Bug

```
Título: [BUG] Breve descrição do problema

Versão: 1.0.0
SO: Windows 11
Python: 3.12.0

## Passos para Reproduzir
1. ...
2. ...
3. ...

## Comportamento Esperado
...

## Comportamento Observado
...

## Logs/Screenshots
...
```

## 🎯 Sugerindo Melhorias

Sugestões de funcionalidades são bem-vindas. Por favor:

1. **Use um título claro e descritivo**
2. **Descreva a motivação** por trás da sugestão
3. **Forneça exemplos** de como a funcionalidade funcionaria
4. **Liste exemplos de aplicações** similares que implementam isto
5. **Nota o impacto** esperado no projeto

### Formato de Sugestão de Melhoria

```
Título: [MELHORIA] Breve descrição

## Motivação
Por que isto seria útil?

## Solução Proposta
Como você imaginaria isso funcionando?

## Alternativas Consideradas
Existem outras formas de resolver este problema?

## Contexto Adicional
Mais informações relevantes
```

## 💻 Processo de Desenvolvimento

### 1. Fork e Clone

```bash
git clone https://github.com/seu-usuario/leitor-desligamentos-cmic.git
cd leitor_desligamentos_cmic
```

### 2. Crie uma Branch

```bash
# Para bug fixes
git checkout -b fix/descricao-do-problema

# Para features
git checkout -b feature/descricao-da-feature
```

### 3. Configure o Ambiente

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
pip install pytest black flake8 isort
```

### 4. Faça suas Mudanças

- Escreva código limpo e bem documentado
- Siga o estilo de código do projeto
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário

### 5. Teste suas Mudanças

```bash
# Executar testes
pytest tests/ -v

# Verificar lint
flake8 . --exclude=venv

# Formatar código
black .
isort .
```

### 6. Commit

```bash
git add .
git commit -m "Tipo: Descrição breve (máx 50 caracteres)"
```

**Tipos de commit recomendados:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Mudanças de formatação (não afetam código)
- `refactor`: Refatoração de código
- `perf`: Melhorias de performance
- `test`: Adição ou alteração de testes

### 7. Push e Pull Request

```bash
git push origin feature/descricao
```

Depois, abra um Pull Request no GitHub com:

- **Título descritivo**
- **Descrição das mudanças**
- **Referência a issues relacionadas** (se houver)
- **Screenshots/gifs** se apropriado

## 📝 Guia de Estilo

### Python

- Siga [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use `black` para formatação automática
- Use `isort` para organizar imports
- Comprimento máximo de linha: 88 caracteres
- Docstrings em todas as funções e classes

### Docstrings

```python
def funcao(parametro: str) -> str:
    """
    Breve descrição do que a função faz.
    
    Descrição mais longa se necessária, explicando
    comportamentos importantes.
    
    Args:
        parametro: Descrição do parâmetro
        
    Returns:
        Descrição do retorno
        
    Raises:
        ValueError: Quando algo dá errado
        
    Example:
        >>> funcao("teste")
        "resultado"
    """
    pass
```

### Comentários

```python
# Comentário para linha de código difícil
resultado = x * 2 + y  # Aqui explicamos a lógica

# Comentários de múltiplas linhas para blocos complexos
# São preferíveis a comentários inline
for i in range(10):
    valor = i * i
    print(valor)
```

## 🧪 Testes

- Toda funcionalidade nova deve ter testes
- Mantenha cobertura acima de 80%
- Use names descritivos para testes

```python
def test_funcao_retorna_valor_esperado():
    """Testa que a função retorna o valor correto."""
    resultado = funcao("entrada")
    assert resultado == "saida esperada"
```

## 📚 Documentação

- Mantenha README.md atualizado
- Adicione exemplos de uso para novas funcionalidades
- Documente comportamentos não-óbvios
- Atualize CHANGELOG.md

## 🔍 Revisão de Código

- PRs serão revisadas antes de merge
- Feedbacks serão construtivos
- Mantenha a discussão profissional
- Seja receptivo a sugestões

## ⚖️ Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

## 📞 Perguntas?

- Abra uma issue com tag `[PERGUNTA]`
- Consulte a documentação existente
- Procure em issues fechadas

---

**Obrigado por contribuir! 🎉**
