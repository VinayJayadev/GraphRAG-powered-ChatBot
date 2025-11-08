from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    OPENROUTER_API_KEY: Optional[str] = None
    BRAVE_API_KEY: Optional[str] = None  # Match the JS implementation
    
    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # RAG Settings
    COLLECTION_NAME: str = "documents"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # Tooling
    USE_MCP: bool = False
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        


_settings_instance = None

def get_settings() -> Settings:
    """Get settings instance. Cache is cleared on import to ensure fresh settings."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
        # Warn if OPENROUTER_API_KEY is not set
        if not _settings_instance.OPENROUTER_API_KEY or _settings_instance.OPENROUTER_API_KEY == "your-openrouter-api-key-here":
            try:
                print("WARNING: OPENROUTER_API_KEY is not set or is using placeholder value.")
                print("Please set OPENROUTER_API_KEY in your .env file to use the chat functionality.")
                print("Get your API key from: https://openrouter.ai")
            except UnicodeEncodeError:
                # Fallback for Windows console encoding issues
                print("WARNING: OPENROUTER_API_KEY is not set or is using placeholder value.")
                print("Please set OPENROUTER_API_KEY in your .env file to use the chat functionality.")
    return _settings_instance

def clear_settings_cache():
    """Clear the settings cache. Useful for testing or when .env changes."""
    global _settings_instance
    _settings_instance = None
