#!/bin/bash

echo "🚀 Iniciando Gerador CVS API"
echo "================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor instale Python 3.8+"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado. Por favor instale pip"
    exit 1
fi

echo "✅ Python e pip encontrados"

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚙️  Criando arquivo .env..."
    cat > .env << EOL
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_USE_SSL=true

# Application Settings
CSV_STORAGE_PATH=./data
LOG_LEVEL=INFO
API_PORT=8000

# Processing Settings
EMAIL_CHECK_INTERVAL=300
MAX_FILE_SIZE_MB=50
EOL
    
    echo "📝 Arquivo .env criado. IMPORTANTE: Configure sua OPENAI_API_KEY!"
    echo "🔑 Edite o arquivo .env e adicione sua chave da OpenAI"
    echo ""
    echo "Para continuar, execute:"
    echo "1. Edite o arquivo .env com sua OPENAI_API_KEY"
    echo "2. Execute novamente: ./start.sh"
    exit 1
fi

# Verificar se OPENAI_API_KEY está configurada
source .env
if [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY não configurada no arquivo .env"
    echo "🔑 Por favor, edite o arquivo .env e adicione sua chave da OpenAI"
    exit 1
fi

echo "✅ Configuração validada"

# Criar diretórios necessários
mkdir -p data logs
echo "📁 Diretórios criados"

# Iniciar API
echo "🌐 Iniciando API na porta 8000..."
echo "📍 API disponível em: http://localhost:8000"
echo "📖 Documentação em: http://localhost:8000/docs"
echo "🛑 Pressione Ctrl+C para parar"
echo ""

python run_api.py