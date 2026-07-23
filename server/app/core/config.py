"""Application configuration loaded from environment / .env.

All settings have sensible demo-mode defaults so the app runs with zero setup.
Provide real values in production via environment variables or a .env file.
"""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# The insecure default signing secret. Production startup refuses to run with this.
DEFAULT_SECRET_KEY = "dev-insecure-secret-change-me"

# Environments that are treated as non-production (relaxed config checks).
NON_PRODUCTION_ENVS = {"development", "dev", "local", "test", "testing"}


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
    secret_key: str = DEFAULT_SECRET_KEY
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

    # --- Background sync ---
    # Freshness SLA: active connections re-sync every N minutes while the server
    # is running (single-instance scheduler; see docs/DEPLOYMENT.md).
    sync_interval_minutes: int = 30
    sync_scheduler_enabled: bool = True
    sync_scheduler_tick_seconds: int = 60

    # --- Integrations ---
    # Demo mode makes every provider return realistic synthetic data so the
    # full app is runnable without external credentials.
    demo_mode: bool = True
    canvas_base_url: str = "https://canvas.instructure.com"
    google_client_id: str = ""
    google_client_secret: str = ""

    # --- LLM extraction (course-website provider) ---
    # Backend-agnostic: point LLM_BASE_URL at any OpenAI-compatible endpoint —
    # Ollama (http://localhost:11434/v1), LM Studio, vLLM, or a hosted provider.
    # Alternatively set ANTHROPIC_API_KEY to use the Anthropic API instead.
    # If neither is set, the course-website provider is demo-only.
    llm_base_url: str = ""
    llm_api_key: str = ""  # optional; local servers like Ollama don't need one
    llm_model: str = ""  # e.g. "qwen2.5:3b" (Ollama) or an Anthropic model id
    anthropic_api_key: str = ""
    # Page-text budget sent to the model. The default fits Ollama's small
    # default context window; raise it for hosted/large-context models.
    llm_max_page_chars: int = 6000

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.frontend_origin]
        if self.extra_cors_origins:
            origins += [o.strip() for o in self.extra_cors_origins.split(",") if o.strip()]
        return [o for o in origins if o]

    @property
    def sqlalchemy_database_url(self) -> str:
        """Normalize the DATABASE_URL for SQLAlchemy + psycopg3.

        Railway (and many providers) hand out ``postgres://`` or ``postgresql://`` URLs,
        which SQLAlchemy maps to the psycopg2 dialect by default. We use psycopg3, so we
        rewrite the scheme to ``postgresql+psycopg://``.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def is_production(self) -> bool:
        """True for any environment not explicitly marked non-production.

        On Railway, ``RAILWAY_ENVIRONMENT`` is set automatically; if the operator
        forgets to set ENVIRONMENT we still treat it as production and fail closed
        rather than silently running with dev defaults.
        """
        if self.environment.lower() in NON_PRODUCTION_ENVS:
            return False
        return True

    @property
    def on_railway(self) -> bool:
        return bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"))

    @property
    def uses_default_secret(self) -> bool:
        return self.secret_key == DEFAULT_SECRET_KEY


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
