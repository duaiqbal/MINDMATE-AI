"""Test that settings fail fast when a required secret is missing.

Each required secret has no default, so constructing Settings without it must
raise a clear pydantic ValidationError naming the missing field.
"""

import pytest
from pydantic import ValidationError

from app.config import Settings

REQUIRED_SECRETS = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_JWT_SECRET",
    "LLM_MODEL_NAME",
    "LLM_TIMEOUT_SECONDS",
]

COMPLETE_ENV = {
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_ANON_KEY": "anon-placeholder",
    "SUPABASE_SERVICE_ROLE_KEY": "service-placeholder",
    "SUPABASE_JWT_SECRET": "jwt-placeholder",
    "LLM_MODEL_NAME": "placeholder-model",
    "LLM_TIMEOUT_SECONDS": "10",
}


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure nothing leaks from the real environment or a local .env.
    for key in REQUIRED_SECRETS:
        monkeypatch.delenv(key, raising=False)


def test_settings_valid_when_all_present(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    for key, value in COMPLETE_ENV.items():
        monkeypatch.setenv(key, value)
    # _env_file=None so a developer's local .env cannot interfere with the test.
    settings = Settings(_env_file=None)
    assert settings.supabase_url == COMPLETE_ENV["SUPABASE_URL"]
    assert settings.llm_timeout_seconds == 10.0


@pytest.mark.parametrize("missing", REQUIRED_SECRETS)
def test_settings_fail_fast_when_secret_missing(
    monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    _clear_env(monkeypatch)
    for key, value in COMPLETE_ENV.items():
        if key == missing:
            continue
        monkeypatch.setenv(key, value)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    # The error clearly names the missing field.
    assert missing.lower() in str(exc_info.value).lower()
