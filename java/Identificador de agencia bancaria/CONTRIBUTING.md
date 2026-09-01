# Contribuindo

Obrigado por contribuir! Este projeto é mantido com padrões profissionais.

## 📋 Antes de Começar

1. Leia o `README.md` para entender o escopo
2. Revise o `DEVELOPMENT.md` para padrões de código
3. Execute os testes localmente: `npm test` / `mvn test`

## 🔄 Fluxo de Contribuição

### 1. Criar uma Branch
```bash
git checkout -b feature/sua-funcionalidade
# ou
git checkout -b fix/seu-bug
```

### 2. Fazer Mudanças
- Mantenha commits pequenos e focados
- Escreva mensagens descritivas
- Certifique-se de que testes passam

### 3. Testes
```bash
# Frontend
npm run type-check

# Backend
mvn test
```

### 4. Enviar Changes
```bash
git push origin feature/sua-funcionalidade
```

## 🎯 Padrões Esperados

- **Código**: Tipagem completa, comentários em lógica complexa
- **Testes**: Novo código deve ter testes correspondentes
- **Documentação**: Atualizar README/docs se mudar comportamento
- **Performance**: Evitar reprocessamentos desnecessários
- **Segurança**: Validar inputs, não expor informações sensíveis

## ⚠️ O Que Não Fazer

- ❌ Enviar código sem testar
- ❌ Commits muito grandes com mudanças não relacionadas
- ❌ Remover funcionalidades sem discussão
- ❌ Adicionar dependências desnecessárias
- ❌ Ignorar eslint/TypeScript errors

## 💬 Dúvidas?

Abra uma issue descrevendo o problema com detalhes.

---

**Obrigado por manter este projeto profissional!**
