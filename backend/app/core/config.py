from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "SchoolAI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super_secret_change_me_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # ------------------------------------------------------------------
    # AI Provider Layer (AI Intelligence Engine)
    # ------------------------------------------------------------------
    # Which provider is used by default. One of: "openai", "gemini", "claude".
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
    # Comma-separated ordered fallback list tried if the primary provider fails
    # after exhausting its retries, e.g. "gemini,claude"
    AI_FALLBACK_PROVIDERS: List[str] = [
        p.strip() for p in os.getenv("AI_FALLBACK_PROVIDERS", "").split(",") if p.strip()
    ]

    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_BASE_URL: str = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")

    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    ANTHROPIC_BASE_URL: str = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")

    AI_REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "30"))
    AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", "2"))
    AI_RETRY_BACKOFF_SECONDS: float = float(os.getenv("AI_RETRY_BACKOFF_SECONDS", "1.0"))
    AI_MAX_OUTPUT_TOKENS: int = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "1200"))

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "schoolai")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "schoolai_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "schoolai_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # Comma-separated list of allowed origins, e.g. "https://app.schoolai.com,https://admin.schoolai.com"
    # Defaults to "*" for local/dev convenience. The API is Bearer-token authenticated
    # (no cookies), so allow_credentials is kept False in main.py to avoid the
    # unsafe/invalid combination of a wildcard origin with credentialed requests.
    CORS_ORIGINS: List[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()
    ]

    class Config:
        case_sensitive = True

settings = Settings()
