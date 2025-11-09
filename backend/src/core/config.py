"""
Configuration management using Pydantic Settings.

This module loads environment variables and provides application configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

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

    # Anthropic API (Claude 3 Sonnet)
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    llm_model: str = Field(
        default="claude-3-sonnet-20240229", env="LLM_MODEL"
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
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    github_rate_limit: int = Field(default=5000, env="GITHUB_RATE_LIMIT")
    twitter_rate_limit: int = Field(default=300, env="TWITTER_RATE_LIMIT")

    # File Upload
    max_upload_size: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
