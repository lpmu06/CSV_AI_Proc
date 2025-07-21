from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Email Configuration
    EMAIL_HOST: str = "imap.gmail.com"
    EMAIL_PORT: int = 993
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_USE_SSL: bool = True
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    
    # Application Settings
    CSV_STORAGE_PATH: str = "./data"
    LOG_LEVEL: str = "INFO"
    API_PORT: int = 8000
    
    # Processing Settings
    EMAIL_CHECK_INTERVAL: int = 300  # seconds
    MAX_FILE_SIZE_MB: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings() 