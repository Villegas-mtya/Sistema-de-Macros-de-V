"""Validaciones iniciales compartidas de Sistema de Macros de V."""

from __future__ import annotations

VALID_VARIATION_MODES = {"fixed", "light", "medium", "high"}
VALID_KEY_SELECTION_MODES = {"simple", "advanced"}


def is_non_negative_number(value: object) -> bool:
    """Indica si un valor puede tratarse como número mayor o igual a cero."""
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def is_positive_integer(value: object) -> bool:
    """Indica si un valor representa una cantidad entera mayor o igual a uno."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return False
    return number >= 1 and str(value).strip() == str(number)


def is_valid_variation_mode(value: object) -> bool:
    """Valida los identificadores internos permitidos para variación de tiempo."""
    return isinstance(value, str) and value in VALID_VARIATION_MODES
