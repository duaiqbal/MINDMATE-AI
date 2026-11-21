"""OpenRouter provider for the LLM gateway, with a model fallback chain.

Returns a plain ``Provider`` callable ``(model, masked_prompt) -> reply``, so the
gateway stays provider-agnostic. Facts used here were checked against the
OpenRouter docs: Bearer auth, ``POST {base}/chat/completions``, and the
``provider.data_collection = "deny"`` routing option, which restricts requests
to providers that do not collect user data.

Fallback: free models are often busy. The primary model is tried first, then
each fallback model in order, but ONLY for "this model is unavailable right
now" errors (429, 404 no endpoint for our data policy, 502, 503). Key or
account errors (401, 402, 403) stop immediately: another model would fail the
same way and waste the free daily quota.

The model that actually answered is stored on ``provider.last_model`` so it
can be logged for reproducibility.

Rules kept here:
* No tools / function calling are ever sent (the gateway has no tool access).
* The API key is never logged or included in error messages.
* Any final error raises, so the gateway falls back to the safe template.
"""

from __future__ import annotations

from collections.abc import Sequence

import httpx

from app.llm.gateway import Provider

MAX_REPLY_TOKENS = 350
# Model unavailable right now -> try the next model in the chain.
FALLBACK_STATUSES = frozenset({404, 429, 502, 503})


class ProviderError(RuntimeError):
    """The provider returned an error or an unusable response."""


def make_openrouter_provider(
    *,
    api_key: str,
    base_url: str,
    timeout_seconds: float,
    fallback_models: Sequence[str] = (),
    transport: httpx.BaseTransport | None = None,
) -> Provider:
    """Build a provider callable bound to one API key and a fallback chain."""
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    def _call(client: httpx.Client, model: str, prompt: str) -> httpx.Response:
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": MAX_REPLY_TOKENS,
            "temperature": 0.7,
            # Only route to providers that do not collect user data.
            "provider": {"data_collection": "deny"},
        }
        return client.post(url, json=body, headers=headers)

    def provider(model: str, prompt: str) -> str:
        chain = [model, *(m for m in fallback_models if m and m != model)]
        errors: list[str] = []
        with httpx.Client(timeout=timeout_seconds, transport=transport) as client:
            for candidate in chain:
                resp = _call(client, candidate, prompt)
                if resp.status_code in FALLBACK_STATUSES:
                    errors.append(f"{candidate}: HTTP {resp.status_code}")
                    continue
                if resp.status_code != 200:
                    # Status code only: never echo headers (they contain the key).
                    raise ProviderError(f"OpenRouter returned HTTP {resp.status_code}")
                try:
                    content = resp.json()["choices"][0]["message"]["content"]
                except (ValueError, KeyError, IndexError, TypeError) as exc:
                    raise ProviderError(
                        "OpenRouter response had no message content"
                    ) from exc
                if not isinstance(content, str) or not content.strip():
                    raise ProviderError("OpenRouter returned an empty reply")
                provider.last_model = candidate  # type: ignore[attr-defined]
                return content.strip()
        raise ProviderError("All models unavailable: " + "; ".join(errors))

    provider.last_model = None  # type: ignore[attr-defined]
    return provider