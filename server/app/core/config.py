"""Application configuration loaded from environment / .env.

All settings have sensible demo-mode defaults so the app runs with zero setup.
Provide real values in production via environment variables or a .env file.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    app_name: str = "Trackable"
    environment: str = "development"
    debug: bool = True

    # --- Security ---
    # NOTE: override in production. This default is for local/demo only.
    secret_key: str = "dev-insecure-secret-change-me"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    algorithm: str = "HS256"
    # Fernet key for encrypting integration secrets at rest. If unset, a key is
    # derived from secret_key (fine for demo; set explicitly in production).
    encryption_key: str | None = None

    # --- Database ---
    database_url: str = "sqlite:///./trackable.db"

    # --- CORS ---
    frontend_origin: str = "http://localhost:5173"
    extra_cors_origins: str = ""  # comma-separated additional origins

    # --- Rate limiting ---
    rate_limit_default: str = "200/minute"
    rate_limit_auth: str = "20/minute"
    rate_limit_sync: str = "10/minute"

    # --- Caching ---
    cache_ttl_seconds: int = 60

    # --- Integrations ---
    # Demo mode makes every provider return realistic synthetic data so the
    # full app is runnable without external credentials.
    demo_mode: bool = True
    canvas_base_url: str = "https://canvas.instructure.com"
    google_client_id: str = ""
    google_client_secret: str = ""

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.frontend_origin]
        if self.extra_cors_origins:
            origins += [o.strip() for o in self.extra_cors_origins.split(",") if o.strip()]
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
