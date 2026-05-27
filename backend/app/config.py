"""
Application configuration using Pydantic BaseSettings.

All environment variables are loaded and validated here.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://adaptlab:adaptlab@db:5432/adaptlab"

    # Kimi API (Moonshot AI)
    KIMI_API_KEY: str = ""
    KIMI_MODEL: str = "moonshot-v1-8k"

    # JWT Authentication
    JWT_SECRET: str = "change-this-to-a-random-secret-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # Judge0 Code Execution
    JUDGE0_URL: str = "http://judge0:2358"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Curriculum
    CURRICULUM_PATH: str = "/app/curriculum"

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
