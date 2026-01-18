"""Configuration management for DELTA platform."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    secret_key: str = Field(..., min_length=32)
    api_version: str = "v1"

    # Database (optional for local dev)
    database_url: str = "sqlite+aiosqlite:///./delta_dev.db"
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis (optional for local dev)
    redis_url: str = "redis://localhost:6379"

    # Fly.io
    fly_api_token: str = ""
    fly_org: str = ""
    fly_region: str = "sjc"  # San Jose, CA

    # JWT Authentication
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Password hashing (Argon2)
    argon2_time_cost: int = 3
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 4

    # Claude API
    anthropic_api_key: str = ""

    # AWS SES (Email)
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-west-2"
    ses_from_email: str = ""
    ses_reply_to: str = ""

    # Twilio (SMS/Voice)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    twilio_sms_rate_limit_per_day: int = 50
    twilio_call_rate_limit_per_day: int = 10

    # Stripe (Payments)
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_free: str = ""
    stripe_price_id_developer: str = ""
    stripe_price_id_pro: str = ""

    # Cloudflare R2 (Storage)
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_endpoint: str = ""
    r2_bucket_name: str = "delta-workspaces"

    # Token Limits
    free_tier_tokens_per_month: int = 1000
    developer_tier_tokens_per_month: int = 10000
    pro_tier_tokens_per_month: int = 100000

    # Agent Limits
    default_agent_memory_mb: int = 512
    max_agent_memory_mb: int = 4096
    default_agent_cpu_cores: int = 1
    max_agent_cpu_cores: int = 4

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Logging
    log_level: str = "INFO"
    sentry_dsn: str = ""


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
