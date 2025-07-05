"""Configuration settings for the Terms & Conditions Analyzer."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
TERMS_DIR = DATA_DIR / "terms"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, VECTOR_STORE_DIR, TERMS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class DatabaseSettings(BaseModel):
    """Database configuration settings."""
    url: str = "sqlite:///data/terms_analyzer.db"
    echo: bool = False

class VectorStoreSettings(BaseModel):
    """Vector store configuration settings."""
    type: str = "chroma"  # Options: chroma, weaviate, etc.
    persist_directory: str = str(VECTOR_STORE_DIR)
    collection_name: str = "terms_embeddings"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

class OpenAISettings(BaseModel):
    """OpenAI API configuration settings."""
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 4000

class TavilySettings(BaseModel):
    """Tavily API configuration settings."""
    api_key: str = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    search_depth: str = "advanced"  # 'basic' or 'advanced'
    include_raw_content: bool = True

class LangChainSettings(BaseModel):
    """LangChain specific settings."""
    debug: bool = False
    verbose: bool = False
    max_concurrency: int = 5

class AppSettings(BaseSettings):
    """Main application settings."""
    app_name: str = "Terms & Conditions Analyzer"
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False
    
    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    openai: OpenAISettings = OpenAISettings()
    tavily: TavilySettings = TavilySettings()
    langchain: LangChainSettings = LangChainSettings()
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )

# Initialize settings
settings = AppSettings()

# Configure logging
import logging
from loguru import logger

logger.add(
    LOGS_DIR / "app.log",
    rotation="10 MB",
    retention="30 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    backtrace=True,
    diagnose=settings.debug
)

# Set up logging for third-party libraries
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Suppress noisy loggers
for logger_name in ["httpx", "httpcore", "openai"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Export settings
__all__ = ["settings", "logger"]
