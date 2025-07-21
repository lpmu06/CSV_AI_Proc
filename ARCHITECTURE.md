# ARQUITETURA DO SISTEMA - AUTOMAÇÃO CSV

## VISÃO GERAL
Sistema automatizado para processar emails com CSVs de fornecedores, enriquecer dados via IA e gerar outputs padronizados.

## COMPONENTES PRINCIPAIS

### 1. EMAIL MONITOR
- **Função**: Verificar inbox, detectar CSVs, fazer download
- **Tech**: Python + imaplib/email
- **Input**: Credenciais de email
- **Output**: Arquivos CSV baixados

### 2. CSV PROCESSOR API
- **Função**: Enriquecer dados usando LLM
- **Tech**: FastAPI + OpenAI + Langchain
- **Input**: CSV bruto
- **Output**: CSV enriquecido

### 3. FILE HANDLER
- **Função**: Gerenciar arquivos (download, storage, cleanup)
- **Tech**: Python + pathlib
- **Storage**: Local filesystem (MVP)

## FLUXO DE DADOS

```
Email Inbox → Monitor → CSV Download → Processor API → Enriched CSV → Storage
```

## STACK TÉCNICO

**Backend:**
- Python 3.11+
- FastAPI (API REST)
- OpenAI API (LLM)
- Langchain (LLM orchestration)

**Infrastructure:**
- Docker + Docker Compose
- Local file storage
- Environment variables

**Development:**
- Poetry (dependency management)
- Black (code formatting)
- Pytest (testing)

## ESTRUTURA DE PROJETO

```
csv-automation/
├── app/
│   ├── core/          # Configurações
│   ├── services/      # Business logic
│   ├── api/           # FastAPI routes
│   └── models/        # Data models
├── tests/
├── docker/
├── data/              # CSV storage
└── docs/
```

## MVP SCOPE

**INCLUÍDO:**
- Monitor email via polling
- Download CSV attachments
- API de enriquecimento via OpenAI
- Output CSV generation
- Basic error handling
- Docker deployment

**NÃO INCLUÍDO (v2):**
- Webhooks
- Database persistence
- Web interface
- Multiple LLM providers
- Advanced monitoring
- Baselinker integration

## DECISÕES TÉCNICAS

1. **Polling vs Webhooks**: Polling para simplicidade no MVP
2. **Storage**: Local files, não database
3. **Authentication**: Env vars, não OAuth
4. **Monitoring**: Logs básicos
5. **Scaling**: Single instance primeiro

## PRÓXIMOS PASSOS

1. Setup inicial do projeto
2. Implementar Email Monitor
3. Criar CSV Processor API
4. Containerização
5. Testes end-to-end 