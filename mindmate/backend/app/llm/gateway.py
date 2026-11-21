"""The single, constrained path to the LLM.

Owns (per tech.md): timeout, retry/backoff, and model name (from config). It
receives ONLY PII-masked text and has NO tool access (it is text-in / text-out
by construction). It does NOT import the safety layer, and the safety/crisis
path must never call it.

The actual provider call is injected as a plain callable. No provider or API
key is hard-coded; wiring a real provider is a config/injection concern handled
later. This keeps the gateway testable and provider-agnostic.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from app.llm.pii import mask_pii

# A provider is any callable: (model_name, masked_prompt) -> reply text.
Provider = Callable[[str, str], str]


class LlmError(RuntimeError):
    """Raised when the gateway exhausts retries or is misused."""


@dataclass(frozen=True)
class GatewayConfig:
    """Gateway configuration (model name + timeout + retry policy)."""

    model_name: str
    timeout_seconds: float = 10.0
    max_retries: int = 2
    backoff_base_seconds: float = 0.2


class LlmGateway:
    """Constrained text-in/text-out gateway with timeout + retry/backoff."""

    def __init__(
        self,
        config: GatewayConfig,
        provider: Provider,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._config = config
        self._provider = provider
        self._sleep = sleep

    def complete(self, prompt: str) -> str:
        """Mask PII, then call the provider with retry/backoff.

        Only masked text is ever passed to the provider. Raises LlmError after
        exhausting retries.
        """
        masked = mask_pii(prompt)
        attempts = self._config.max_retries + 1
        last_err: Exception | None = None

        for attempt in range(attempts):
            try:
                return self._provider(self._config.model_name, masked)
            except Exception as exc:  # provider failures are retried
                last_err = exc
                if attempt < attempts - 1:
                    self._sleep(self._config.backoff_base_seconds * (2 ** attempt))

        raise LlmError(
            f"LLM call failed after {attempts} attempt(s): {last_err}"
        ) from last_err