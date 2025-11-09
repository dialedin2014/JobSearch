"""
Configuration management using Pydantic Settings.

This module loads environment variables and provides application configuration.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv

# Get the backend directory (two levels up from this file)
BACKEND_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"

# Load .env file BEFORE importing pydantic settings
# Pydantic will prioritize actual environment variables over .env values
load_dotenv(ENV_FILE, override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = Field(default="Dream Job Ally Deduction", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS",
    )

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Anthropic API (Claude Sonnet 4.5)
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    llm_model: str = Field(
        default="claude-sonnet-4-5-20250929", env="LLM_MODEL"
    )
    llm_max_tokens: int = Field(default=4096, env="LLM_MAX_TOKENS")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_cache_ttl: int = Field(default=86400, env="LLM_CACHE_TTL")  # 24 hours

    # External APIs (Optional)
    github_api_token: str = Field(default="", env="GITHUB_API_TOKEN")
    twitter_api_key: str = Field(default="", env="TWITTER_API_KEY")
    twitter_api_secret: str = Field(default="", env="TWITTER_API_SECRET")
    linkedin_api_key: str = Field(default="", env="LINKEDIN_API_KEY")

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=100, env="RATE_LIMIT_PER_MINUTE")
    github_rate_limit: int = Field(default=5000, env="GITHUB_RATE_LIMIT")
    twitter_rate_limit: int = Field(default=300, env="TWITTER_RATE_LIMIT")

    # File Upload
    max_upload_size: int = Field(
        default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")


# Global settings instance
settings = Settings()
