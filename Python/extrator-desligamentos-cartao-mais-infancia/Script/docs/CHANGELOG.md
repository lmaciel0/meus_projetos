# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Adicionado

- Versão inicial do Leitor de Desligamentos CMIC
- Extração de texto de PDFs usando pdfplumber
- Suporte a OCR com pytesseract para PDFs escaneados
- Parser para campos: MUNICIPIO, CPF, NIS, NOME, MOTIVO
- Exportação para XLSX com formatação completa
- Exportação para CSV com separador ponto-e-vírgula
- Interface CLI simples com argparse
- Testes unitários para parser de campos
- Documentação em português (README.md)
- Scripts de ajuda para Windows e Linux/macOS
- Suporte a múltiplas páginas em PDFs
- Preservação de zeros à esquerda em CPF e NIS
- Coluna de auditoria (ARQUIVO_ORIGEM e STATUS_EXTRACAO)
- Classificação automática de registros que precisam revisão
- Setup.py para instalação como pacote Python

### Características Principais

- ✅ Extração robusta de campos específicos
- ✅ Normalização de texto e caracteres especiais
- ✅ Suporte a PDFs nativos e escaneados
- ✅ Formatação profissional de planilhas
- ✅ Relatório detalhado de processamento
- ✅ Código bem estruturado e testado
- ✅ Documentação completa

## Roadmap Futuro

### Planejado para v1.1

- [ ] Interface gráfica (GUI) com Tkinter
- [ ] Processamento em background com Celery
- [ ] Webhooks para integração com sistemas externos
- [ ] Suporte a mais formatos de exportação (JSON, Parquet)
- [ ] Validação customizável de dados
- [ ] Cache de PDFs processados

### Planejado para v1.2

- [ ] API REST para processamento
- [ ] Dashboard web de monitoramento
- [ ] Histórico de processamento em banco de dados
- [ ] Suporte a múltiplos idiomas na extração
- [ ] Relatórios em PDF

### Considerações Futuras

- Integração com sistemas de arquivamento
- Assinatura digital de arquivos exportados
- Backup automático de resultados
- Notificações por email de problemas
- Versionamento de dados processados

---

## Guia de Versionamento

- **Versão Major (X.0.0)**: Mudanças incompatíveis na API
- **Versão Minor (X.Y.0)**: Novas funcionalidades, compatível
- **Versão Patch (X.Y.Z)**: Correção de bugs

## Como Contribuir

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para mais informações.
