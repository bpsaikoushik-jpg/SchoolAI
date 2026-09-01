from pydantic_settings import BaseSettings
from typing import List
import os


class Settings:
    PROJECT_NAME: str = "SchoolAI"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = os.getenv(
        "JWT_SECRET",
        "super_secret_change_me_in_production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # ------------------------------------------------------------------
    # AI Provider Layer
    # ------------------------------------------------------------------
    # Gemini is the ONLY AI provider.
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )
    GEMINI_BASE_URL: str = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta"
    )

    AI_REQUEST_TIMEOUT_SECONDS: float = float(
        os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "30")
    )
    AI_MAX_RETRIES: int = int(
        os.getenv("AI_MAX_RETRIES", "2")
    )
    AI_RETRY_BACKOFF_SECONDS: float = float(
        os.getenv("AI_RETRY_BACKOFF_SECONDS", "1.0")
    )
    AI_MAX_OUTPUT_TOKENS: int = int(
        os.getenv("AI_MAX_OUTPUT_TOKENS", "1200")
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL

        if url.startswith("postgresql://"):
            url = url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        url = url.replace(
            "?sslmode=require&channel_binding=require",
            ""
        )
        url = url.replace("&sslmode=require", "")
        url = url.replace("?sslmode=require", "")
        url = url.replace("&channel_binding=require", "")
        url = url.replace("?channel_binding=require", "")

        return url

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    # Comma-separated list of allowed origins.
    CORS_ORIGINS: List[str] = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "*").split(",")
        if o.strip()
    ]


settings = Settings()
