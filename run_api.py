#!/usr/bin/env python3
"""
Script para executar a API localmente
"""

import uvicorn
import os
import sys
from pathlib import Path

def setup_environment():
    """Setup environment variables for local development"""
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating a template...")
        
        template = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (for production)
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
"""
        
        with open(".env", "w") as f:
            f.write(template)
        
        print("📝 Created .env file template. Please update with your values.")
        print("🔑 Don't forget to add your OPENAI_API_KEY!")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def main():
    """Main function"""
    print("🚀 Starting CSV Processing API...")
    
    # Setup environment
    if not setup_environment():
        print("❌ Please update the .env file and run again.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not configured in .env file")
        print("🔑 Please add your OpenAI API key to the .env file")
        sys.exit(1)
    
    print("✅ Environment configured successfully")
    print("🌐 Starting API server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    # Run the API
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()