from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # App
    env: str = "dev"
    dev_auth_bypass: bool = False
    jwt_secret: str = "change-me"
    jwt_expires_minutes: int = 10080
    default_language: str = "ru"
    cors_origins: str = "http://localhost:5173,https://localhost:5173"

    # Telegram
    bot_token: str = ""
    telegram_admin_ids: str = ""
    support_telegram: str = ""  # default admin @username for "not found" contact (editable in admin panel)
    miniapp_url: str = "https://localhost:5173"
    bot_mode: str = "polling"  # "polling" | "webhook"
    public_base_url: str = "http://localhost:8000"
    webhook_secret: str = "change-me-webhook-secret"

    # Database
    database_url: str = "postgresql+asyncpg://truckbot:truckbot@localhost:5432/truckbot"
    database_url_sync: str = "postgresql+psycopg://truckbot:truckbot@localhost:5432/truckbot"

    # Marketplace
    default_commission_percent: float = 7.0
    default_delivery_cost: float = 0.0

    # Master (usta) bonus payouts
    payout_period_days: int = 12
    payout_check_interval_seconds: int = 3600

    # Payments (stubs)
    click_merchant_id: str = ""
    click_secret_key: str = ""
    payme_merchant_id: str = ""
    payme_secret_key: str = ""
    uzum_merchant_id: str = ""
    uzum_secret_key: str = ""

    @field_validator("default_language")
    @classmethod
    def _lang(cls, v: str) -> str:
        return v if v in ("ru", "uz") else "ru"

    @property
    def admin_ids(self) -> set[int]:
        ids: set[int] = set()
        for part in self.telegram_admin_ids.split(","):
            part = part.strip()
            if part.isdigit():
                ids.add(int(part))
        return ids

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_prod(self) -> bool:
        return self.env.lower() in ("prod", "production")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
