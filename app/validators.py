"""Validaciones iniciales compartidas de Sistema de Macros de V."""

from __future__ import annotations

from collections.abc import Mapping

from app.key_mapper import validate_key

VALID_VARIATION_MODES = {"fixed", "light", "medium", "high"}
VALID_KEY_SELECTION_MODES = {"simple", "advanced"}
REQUIRED_ACTION_FIELDS = {"key", "base_delay", "variation_mode"}


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


def validate_action_key(key: object) -> bool:
    """Valida el campo ``key`` de una acción básica de macro."""
    return validate_key(key)


def validate_action_data(action: object) -> bool:
    """Valida la estructura mínima de una acción de teclado de Fase 3.

    La acción esperada todavía es simple: ``key`` debe ser una tecla soportada,
    ``base_delay`` un número mayor o igual a cero, y ``variation_mode`` uno de los
    modos internos conocidos. Esta validación no guarda, importa ni ejecuta
    macros; solo comprueba datos básicos.
    """
    if not isinstance(action, Mapping):
        return False

    if not REQUIRED_ACTION_FIELDS.issubset(action):
        return False

    return (
        validate_action_key(action["key"])
        and is_non_negative_number(action["base_delay"])
        and is_valid_variation_mode(action["variation_mode"])
    )
