"""
Application configuration.

Loads environment variables from the .env file and makes them available
as a Python object. If a required variable is missing, the app will
fail immediately at startup with a clear error message — instead of
crashing mysteriously later when the variable is first used.

Uses pydantic-settings, which:
1. Reads from the .env file automatically
2. Validates types (e.g., ensures APP_ENV is a string)
3. Provides defaults where appropriate

WHY THIS FILE EXISTS:
- Centralizes all configuration in one place
- Makes it impossible to accidentally use a raw string like "APP_NAME"
  scattered throughout the code
- If removed, every file would need to read os.environ directly,
  which is error-prone and hard to maintain
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings, loaded from environment variables."""

    # Application metadata
    APP_NAME: str = "FitMind AI"
    APP_ENV: str = "development"

    # Gemini API key — not needed until Phase 3, so it has a default
    GEMINI_API_KEY: str = "not-set-yet"

    # JWT configuration
    JWT_SECRET: str = "local-insecure-secret" # In prod, override via .env
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Production security
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    LOG_LEVEL: str = "INFO"

    def model_post_init(self, __context):
        if self.APP_ENV == "production" and self.JWT_SECRET == "local-insecure-secret":
            raise ValueError("JWT_SECRET must be set in production")

    # Tell pydantic-settings to read from .env and .env.local (local overrides)
    # Files listed later take higher priority, so .env.local overrides .env
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore any extra variables in .env we don't use
    )


# Create a single settings instance that the entire app imports
# Usage: from app.config import settings
settings = Settings()
