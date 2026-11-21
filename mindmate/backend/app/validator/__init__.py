"""Output validator + template fallback (enforces product hard-rules)."""

from app.validator.output_validator import (
    ValidationResult,
    validate_or_fallback,
    validate_reply,
)

__all__ = ["ValidationResult", "validate_reply", "validate_or_fallback"]