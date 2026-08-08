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

    # Tell pydantic-settings to read from the .env file in the backend/ folder
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore any extra variables in .env we don't use
    )


# Create a single settings instance that the entire app imports
# Usage: from app.config import settings
settings = Settings()
