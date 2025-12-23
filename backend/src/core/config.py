from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Database settings
    DATABASE_URL: str
    NEON_DATABASE_URL: Optional[str] = None

    # Vector database settings
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # LLM settings
    GEMINI_API_KEY: str
    LLM_PROVIDER: str = "gemini"  # gemini or openai

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application settings
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]  # Should be restricted in production

    class Config:
        env_file = ".env"


settings = Settings()