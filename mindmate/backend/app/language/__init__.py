"""Language utilities: Roman Urdu normalization + rule-based language ID."""

from app.language.identifier import LANG_ID_VERSION, LangResult, identify
from app.language.normalizer import NORMALIZER_VERSION, normalize

__all__ = [
    "normalize",
    "NORMALIZER_VERSION",
    "identify",
    "LangResult",
    "LANG_ID_VERSION",
]