"""Application settings loaded from environment variables.

Rules (see .kiro/steering/tech.md):
- Secrets live only in environment variables.
- Secret fields have NO defaults: a missing required value fails fast with a
  clear error, rather than silently using an insecure default.
- APP_ENV is non-secret and may default to "development".
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings.

    Loaded from environment variables (and a local .env if present). Field
    names are case-insensitive against env var names.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Non-secret, safe default.
    app_env: str = Field(default="development")

    # --- Secrets: required, no defaults (startup fails if missing) ---
    supabase_url: str = Field(...)
    supabase_anon_key: str = Field(...)
    supabase_service_role_key: str = Field(...)
    supabase_jwt_secret: str = Field(...)

    # --- LLM gateway config (required so the one gateway is always configured) ---
    llm_model_name: str = Field(...)
    llm_timeout_seconds: float = Field(...)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Raises pydantic.ValidationError with a clear message if a required
    environment variable is missing.
    """
    return Settings()


class CorsSettings(BaseSettings):
    """Browser origins allowed to call the API (non-secret).

    Kept separate from Settings so the server can start without secrets.
    Comma-separated list, e.g. "http://localhost:5173,https://app.example".
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    cors_allow_origins: str = Field(default="http://localhost:5173")

    def origins(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]
