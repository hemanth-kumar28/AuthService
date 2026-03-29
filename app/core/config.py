"""
Application settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from .env file."""

    # ── App ────────────────────────────────────────────────────
    APP_NAME: str = "AuthService"
    DEBUG: bool = False

    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5431/auth_service_db",
        description="PostgreSQL connection string",
    )
    TEST_DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5431/auth_service_test_db",
        description="PostgreSQL connection string for tests",
    )

    # ── JWT ────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(
        default="CHANGE-ME-TO-A-RANDOM-SECRET-KEY-IN-PRODUCTION",
        description="Secret used to sign JWT tokens",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton instance
settings = Settings()
