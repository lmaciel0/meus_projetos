# Guia de Desenvolvimento

## 📋 Padrões de Código

### TypeScript/React
- Usar Type Safety: sempre tipifique funções, props e estado
- Comentários: documente funções complexas ou lógica não óbvia
- Nomes: use nomes descritivos, camelCase para variáveis/funções
- Componentes: mantenha componentes simples e focados

### Java/Spring Boot
- Padrão MVC: Controller → Service → Repository
- DTOs para respostas da API
- Validação com `@Valid` e Bean Validation
- Logging apropriado para debug e monitoramento

## 🔧 Desenvolvimento Local

### Setup Inicial

```bash
# Backend
cd backend
mvn clean install

# Frontend
cd frontend
npm install
```

### Executar Localmente

```bash
# Terminal 1: Backend
cd backend
mvn spring-boot:run

# Terminal 2: Frontend
cd frontend
npm run dev
```

Acesse: `http://localhost:5173`

### Build de Produção

```bash
# Backend
mvn clean package

# Frontend
npm run build
npm run preview
```

## 🧪 Testes

```bash
# Backend
mvn test

# Frontend
npm run type-check  # Verificação de tipos TypeScript
```

## 📝 Commits

Mantenha mensagens claras e descritivas:

```
feat: adiciona nova funcionalidade
fix: corrige bug em componente X
docs: atualiza README
style: melhora formatação de código
refactor: reorganiza estrutura de diretórios
test: adiciona testes para funcionalidade Y
chore: atualiza dependências
```

## 🚀 Deployments

### Preparação

1. Garantir que todos os testes passam
2. Atualizar versões em `pom.xml` e `package.json`
3. Documentar mudanças significativas
4. Fazer commit e tag com versão

### Build Final

```bash
# Backend (JAR executável)
mvn clean package -DskipTests

# Frontend (Static files)
npm run build
```

## 🐛 Debugging

### Backend
```bash
mvn spring-boot:run -Dspring-boot.run.arguments="--logging.level.com.banco=DEBUG"
```

### Frontend
Use DevTools do navegador (F12) para:
- Inspecionar elementos React
- Console para logs
- Network para requisições da API

## 📚 Recursos

- [Spring Boot Docs](https://spring.io/projects/spring-boot)
- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite Guide](https://vitejs.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Dúvidas?** Consulte a documentação nos arquivos `docs/` ou execute o script de inicialização.
