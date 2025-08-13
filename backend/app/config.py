from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="sla-breach-warning-system")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Security
    secret_key: str = Field(default="dev-secret-change")
    access_token_expire_minutes: int = Field(default=60 * 12)
    cors_origins: str = Field(default="*")

    # Database (override with DATABASE_URL if provided)
    database_url: str | None = None
    postgres_host: str = Field(default="db")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="sla_db")
    postgres_user: str = Field(default="sla_user")
    postgres_password: str = Field(default="sla_pass")

    # Redis / Celery
    redis_url: str = Field(default="redis://redis:6379/0")
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    # Notifications
    smtp_host: str = Field(default="mailhog")
    smtp_port: int = Field(default=1025)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_from_email: str = Field(default="alerts@example.local")

    slack_webhook_url: str | None = None

    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_from_number: str | None = None

    demo_mode: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def sync_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


settings = Settings()
