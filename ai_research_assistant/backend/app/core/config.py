import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
MODELS_DIR = BASE_DIR / "backend" / "models"
DB_PATH = DATA_DIR / "knowledge_base.db"

# Ensure required directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Research & Knowledge Assistant"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Storage & DB
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    UPLOADS_DIR: Path = UPLOADS_DIR
    MODELS_DIR: Path = MODELS_DIR
    
    # RAG & Chunking Config
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # LLM Settings (Configurable for Gemini, OpenAI, or Local Grounded RAG)
    LLM_PROVIDER: str = "local"  # "local", "gemini", "openai"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
