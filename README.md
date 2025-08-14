# 🚀 Gerador CVS - Sistema de Processamento Automático

Sistema completo para processamento automatizado de arquivos CSV com enriquecimento de dados usando IA (OpenAI + LangChain).

## 📋 Visão Geral

### 🎯 Funcionalidades Principais

- ✅ **Monitoramento de Email**: Recebe arquivos CSV automaticamente por email (IMAP)
- ✅ **Processamento IA**: Enriquece dados seguindo regras de negócio específicas
- ✅ **API REST**: Endpoints para upload e processamento manual
- ✅ **Docker**: Containerização completa com Docker Compose
- ✅ **Validação**: Modelos Pydantic para validação de dados
- ✅ **Fallback**: Sistema robusto com dados padrão se IA falhar

### 🏗️ Arquitetura do Sistema

```
Email Monitor ──→ CSV Download ──→ API Processing ──→ Enriched Output
     │                │                    │                │
   IMAP/SSL       File Storage      OpenAI + LangChain   CSV Export
```

## 🛠️ Instalação e Configuração

### 1. Preparação do Ambiente

```bash
# Clone do projeto
git clone <repository-url> gerador_CVS
cd gerador_CVS

# Instalar dependências
pip install -r requirements.txt

# Criar diretórios necessários
mkdir -p data logs
```

### 2. Configuração de Variáveis de Ambiente

```bash
# Criar arquivo de configuração
cp .env.example .env
# Editar com suas credenciais
```

**Configurações obrigatórias (.env):**
```env
# OpenAI Configuration (OBRIGATÓRIO)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email Configuration (Para monitoramento automático)
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password  # Use App Password para Gmail
EMAIL_USE_SSL=true

# Application Settings
CSV_STORAGE_PATH=./data
LOG_LEVEL=INFO
API_PORT=8000
EMAIL_CHECK_INTERVAL=300  # Verifica emails a cada 5 minutos
MAX_FILE_SIZE_MB=50
```

**⚠️ Importante para Gmail:**
1. Ative a verificação em 2 etapas
2. Gere uma senha de app em: https://myaccount.google.com/apppasswords
3. Use a senha de 16 caracteres gerada (não sua senha normal)

### 3. Execução do Sistema

#### Opção 1: Docker Compose (Recomendado)
```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Parar serviços
docker-compose down
```

#### Opção 2: Execução Manual
```bash
# Terminal 1 - API
python run_api.py

# Terminal 2 - Monitor de Email
python -m app.services.email_monitor
```

### 4. Verificar Funcionamento

#### Teste via API (Manual)
```bash
# Health check
curl http://localhost:8000/health

# Processar CSV
curl -X POST "http://localhost:8000/process-csv" \
  -F "file=@examples/input/Carga CMNS.csv" \
  -o "output_enriquecido.csv"
```

#### Teste via Email (Automático)
1. Envie um email para o endereço configurado
2. Anexe um arquivo CSV no formato de entrada
3. Aguarde o processamento (verifica a cada 5 minutos)
4. Arquivo enriquecido será salvo em `data/enriched_*.csv`

## 📡 API Endpoints

### Health Check
```http
GET /health
Response: {"status": "healthy", "service": "csv-automation"}
```

### Processar CSV
```http
POST /process-csv
Content-Type: multipart/form-data
Body: file (CSV)
Response: Arquivo CSV enriquecido para download
```

### Listar Arquivos
```http
GET /files
Response: {"files": ["input_file1.csv", "enriched_file1.csv"]}
```

### Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Formato dos Dados

### Entrada (CSV)
```csv
Referencia,Descricao,Quantidade Estoque,Preço de Venda,Preço de Custo,SKU,EAN
9501473100,9501473100 MOLA VARETA FREIO,2,"R$ 3,83","R$ 2,55",CMNS0483KLE,7897925504835
90084041000,90084041000 PARAFUSO FIX PINHAO,2,"R$ 5,16","R$ 3,44",CMNS0485KLE,7897925504859
```

### Saída (CSV Enriquecido - Formato BaseBlinker)
```csv
ID_produto;ID_OEM;Nome do Produto (BR);ID do Fabricante;Quantidade (Padrão);EAN;SKU;Nome da categoria;Preço (Padrão (BRL));Preço de Compra;Custo (médio);Peso;Descrição (BR);Descrição adicional 1 (BR);Descrição adicional 2 (BR);Nome do fabricante;Altura;Comprimento;Largura;Campo adicional - Tipo de unidade;Tipo de unidade;Campo adicional - Código da origem;Código da origem;Campo adicional - Código do fabricante;Código do fabricante;Parâmetro - NCM (BR);NCM;Parâmetro - Origin Type (BR);Parâmetro - Origin Detail (BR);Campo adicional - NCM
CMNS0483KLE;9501473100;Mola vareta freio Honda Genuíno;9501473100;2;7897925504835;CMNS0483KLE;Peças de Freio Moto;3.83;2.55;2.55;0.05;Mola vareta freio original Honda SKU: LK CMNS0483KLE;incluir texto;Descrição do Produto: Mola vareta freio Aplicação (Compatibilidade de Modelos e Ano): CG150, CG125, Titan Descrição Técnica: mola de aço Marca: Honda Garantia: 3 meses Data: 2025-01-15 Conteúdo da Embalagem: 1 UND de mola Dimensões em cm (Altura x Comprimento x Largura): 1.0x10.0x1.0 Peso (kg): 0.05 Código SKU: CMNS0483KLE Código do Fabricante/Referência: 9501473100 NCM: 7318.15.00 Descrição NCM: Porcas e parafusos de metal comum Op: LK;Honda;1.0;10.0;1.0;un;un;0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8;0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8;9501473100;9501473100;7318.15.00;7318.15.00;0;Reseller;7318.15.00
```

## 🔄 Fluxo de Processamento

### Processamento Automático (Email)
1. **Monitor de Email** verifica inbox a cada 5 minutos
2. **Detecta CSVs** em anexos de emails não lidos
3. **Download automático** para pasta `data/`
4. **Processamento IA** linha por linha seguindo regras de negócio
5. **Output enriquecido** salvo como `data/enriched_*.csv`

### Processamento Manual (API)
1. **Upload CSV** via endpoint `/process-csv` ou Swagger UI
2. **Processamento IA** usando OpenAI + LangChain
3. **Download direto** do arquivo enriquecido

### Regras de Enriquecimento
- **Nome do Produto**: Remove referência + adiciona "Honda Genuíno" (máx 60 chars)
- **Categorização**: Específica por tipo (Parafusos Moto, Kit Revisão Moto, etc.)
- **NCM**: Códigos fiscais corretos por categoria
- **Dimensões/Peso**: Estimativas realistas baseadas no tipo de peça
- **Descrição Adicional 2**: Template completo seguindo regras de negócio

## 📁 Estrutura do Projeto

```
gerador_CVS/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                 # Configurações da aplicação
│   ├── models/
│   │   ├── __init__.py
│   │   └── csv_models.py            # Modelos Pydantic para validação
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_agent.py              # Agente IA com LangChain + OpenAI
│   │   ├── csv_processor.py         # Processador principal de CSV
│   │   └── email_monitor.py         # Monitor de emails IMAP
│   ├── __init__.py
│   └── main.py                      # API FastAPI
├── docker/
│   ├── docker-compose.yml           # Orquestração de serviços
│   └── Dockerfile                   # Imagem Docker
├── data/                            # Armazenamento de CSVs (gitignored)
│   ├── input_*.csv                  # Arquivos de entrada
│   └── enriched_*.csv               # Arquivos processados
├── logs/                            # Logs da aplicação (gitignored)
├── examples/
│   ├── input/
│   │   └── Carga CMNS.csv          # Exemplo de entrada
│   └── output/
│       └── output.csv              # Exemplo de saída esperada
├── prompts/
│   ├── prompt_enriquecimento_produtos.txt
│   └── prompt_universal.txt
├── scripts/                        # Scripts auxiliares
├── .env.example                    # Template de variáveis de ambiente
├── .gitignore                      # Regras do Git
├── README.md                       # Este arquivo
├── regras_de_negocio.txt          # Regras de enriquecimento de dados
├── requirements.txt               # Dependências Python
├── run_api.py                     # Script para executar a API
└── start.sh                       # Script de inicialização automática
```

## 🔧 Status do Desenvolvimento

### Componentes Implementados
- ✅ **API FastAPI**: Funcionando completamente
- ✅ **CSV Processor**: Funcionando com OpenAI + LangChain
- ✅ **AI Agent**: Enriquecimento seguindo regras de negócio
- ✅ **Email Monitor**: Funcionando com IMAP/SSL
- ✅ **Docker**: Testado e funcionando
- ✅ **Modelos Pydantic**: Validação de dados
- ✅ **Fallback System**: Sistema robusto com dados padrão

### Tecnologias Utilizadas
- **Backend**: FastAPI + Python 3.11
- **IA**: OpenAI GPT-4o-mini + LangChain
- **Email**: IMAP/SSL com imaplib
- **Validação**: Pydantic v2
- **Containerização**: Docker + Docker Compose
- **Processamento**: Pandas + asyncio

## 📊 Performance e Monitoramento

### Métricas de Performance
- **Processamento**: ~1-2 segundos por linha
- **Rate Limiting**: 0.5s delay entre requisições IA
- **Timeout**: 5 minutos para processamento completo
- **Fallback**: Dados padrão se IA falhar
- **Email Check**: A cada 5 minutos (configurável)

### Monitoramento de Logs
```bash
# Docker Compose
docker-compose logs -f

# Logs específicos
docker-compose logs -f email-monitor
docker-compose logs -f csv-processor

# Execução manual
tail -f logs/app.log
```

### Armazenamento de Arquivos
- **CSVs de entrada**: `./data/input_*.csv`
- **CSVs processados**: `./data/enriched_*.csv`
- **Logs da aplicação**: `./logs/`
- **Arquivos de exemplo**: `./examples/`

## ⚙️ Configurações Avançadas

### Provedores de Email Suportados
```env
# Gmail (Recomendado)
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USE_SSL=true

# Outlook/Hotmail
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993
EMAIL_USE_SSL=true

# Yahoo
EMAIL_HOST=imap.mail.yahoo.com
EMAIL_PORT=993
EMAIL_USE_SSL=true
```

### Configurações de IA
- **Modelo**: GPT-4o-mini (otimizado para custo/performance)
- **Temperatura**: 0.1 (respostas consistentes)
- **Max Tokens**: 4000 por requisição
- **Processamento**: Linha por linha com delay de 0.5s

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação de Email
```
ERROR: [AUTHENTICATIONFAILED] Invalid credentials
```
**Solução:**
- Para Gmail: Use senha de app (não senha normal)
- Ative verificação em 2 etapas primeiro
- Gere senha de app em: https://myaccount.google.com/apppasswords

#### 2. Erro de API Key OpenAI
```
ERROR: OPENAI_API_KEY not configured
```
**Solução:**
- Adicione sua chave OpenAI no arquivo `.env`
- Verifique se a chave está ativa e tem créditos

#### 3. Problemas de Conexão API
```bash
# Verificar se API está rodando
curl http://localhost:8000/health

# Testar processamento
curl -X POST "http://localhost:8000/process-csv" \
  -F "file=@examples/input/Carga CMNS.csv" \
  -o "test_output.csv"
```

#### 4. Problemas de Armazenamento
```bash
# Criar diretórios necessários
mkdir -p data logs

# Verificar permissões (Linux/Mac)
chmod 755 data/

# Verificar espaço em disco
df -h .  # Linux/Mac
```

## 🚀 Deploy e Produção

### Configurações de Segurança
- **Variáveis de Ambiente**: Todas as credenciais no arquivo `.env`
- **API Keys**: Rotacione chaves OpenAI regularmente
- **Autenticação Email**: Use senhas de app específicas
- **Armazenamento Local**: Arquivos processados localmente

### Monitoramento e Manutenção
- **Logs**: Armazenados em `./logs/` com rotação automática
- **Rastreamento**: Pares input/output preservados
- **Error Handling**: Sistema com fallback robusto
- **Health Check**: Endpoint `/health` para monitoramento

### Escalabilidade
- **Processamento**: Otimizado para arquivos até 50MB
- **Rate Limiting**: Controle de requisições para IA
- **Timeout**: 5 minutos máximo por arquivo
- **Memory**: Processamento streaming para arquivos grandes

## 📞 Suporte e Documentação

### Arquivos de Referência
- **`regras_de_negocio.txt`**: Regras detalhadas de enriquecimento
- **`ARCHITECTURE.md`**: Documentação técnica da arquitetura
- **`examples/`**: Exemplos de entrada e saída esperada

### Para Dúvidas ou Problemas
1. Verifique os logs em `docker-compose logs -f`
2. Teste com arquivo de exemplo em `examples/input/`
3. Valide configurações no arquivo `.env`
4. Consulte o endpoint `/health` para status
