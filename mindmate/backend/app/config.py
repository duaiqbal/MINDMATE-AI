"""Application settings loaded from environment variables.

Rules (see .kiro/steering/tech.md):
- Secrets live only in environment variables.
- Secret fields have NO defaults: a missing required value fails fast with a
  clear error, rather than silently using an insecure default.
- APP_ENV is non-secret and may default to "development".
"""

from functools import lru_cache

from pydantic import Field, SecretStr
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


class LlmSettings(BaseSettings):
    """LLM provider settings (OpenRouter).

    The API key is optional: without it the chat endpoint uses the safe
    template fallback. The key is a SecretStr so it never appears in logs or
    reprs. The model must be an open-weight model; the default is a free
    OpenRouter variant (free variants rotate, so it stays configurable).
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    openrouter_api_key: SecretStr | None = Field(default=None)
    llm_model_name: str = Field(default="google/gemma-4-31b-it:free")
    llm_timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    # Tried in order when the primary model is busy. The ERNIE model's license
    # is UNVERIFIED (see docs/decisions/0001-llm-provider.md).
    llm_fallback_models: str = Field(
        default="google/gemma-4-26b-a4b-it:free,baidu/ernie-5.5-flash-preview:free"
    )
    # Each retry re-runs the whole chain; keep it low to save the free quota.
    llm_max_retries: int = Field(default=1, ge=0, le=5)
    llm_base_url: str = Field(default="https://openrouter.ai/api/v1")

    def fallbacks(self) -> list[str]:
        """Fallback model ids, in order, without blanks or duplicates."""
        seen: list[str] = []
        for m in self.llm_fallback_models.split(","):
            m = m.strip()
            if m and m != self.llm_model_name and m not in seen:
                seen.append(m)
        return seen

    def api_key(self) -> str | None:
        """The key as plain text, or None when unset or blank."""
        if self.openrouter_api_key is None:
            return None
        value = self.openrouter_api_key.get_secret_value().strip()
        return value or None
