"""
Configuration management using Pydantic settings.
Loads environment variables from .env file.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # Database Configuration
    POSTGRES_USER: str = "agentuser"
    POSTGRES_PASSWORD: str = "agentpass"
    POSTGRES_DB: str = "agentsandbox"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Encryption passphrase for API keys
    ENCRYPTION_KEY: str = "change-this-to-a-secure-key-in-production"

    # OpenAI Configuration
    OPENAI_API_KEY: str = ""

    # Anthropic Configuration
    ANTHROPIC_API_KEY: str = ""

    # CORS Origins
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # File Upload Limits
    MAX_UPLOAD_SIZE_MB: int = 1
    ALLOWED_EXTENSIONS: List[str] = ["txt", "json", "pdf", "docx"]

    # RAG Configuration
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 3

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 100
    MAX_TOKENS_PER_HOUR: int = 10000

    # Config Storage
    CONFIG_DIR: str = "./configs"

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Synchronous database URL for migrations."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Create config directory if it doesn't exist
os.makedirs(settings.CONFIG_DIR, exist_ok=True)
