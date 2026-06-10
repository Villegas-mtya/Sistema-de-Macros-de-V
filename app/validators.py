"""Validaciones compartidas de Sistema de Macros de V.

La Fase 4 mantiene validaciones simples y explícitas para que el almacenamiento
JSON pueda rechazar macros incompletas antes de guardarlas, importarlas o
exportarlas. Este módulo no ejecuta macros ni interpreta acciones en tiempo real.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.key_mapper import validate_key

VALID_VARIATION_MODES = {"fixed", "light", "medium", "high"}
VALID_KEY_SELECTION_MODES = {"simple", "advanced"}
VALID_EXECUTION_MODES = {"real", "test_log", "test_keys"}

REQUIRED_ACTION_FIELDS = {"key", "base_delay", "variation_mode"}
REQUIRED_MACRO_FIELDS = {
    "app",
    "version",
    "actions",
    "initial_delay",
    "repetitions",
    "infinite",
    "cooldown_base",
    "cooldown_variation",
    "execution_mode",
    "key_selection_mode",
}


def is_non_negative_number(value: object) -> bool:
    """Indica si un valor puede tratarse como número mayor o igual a cero."""
    if isinstance(value, bool):
        return False

    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def is_positive_integer(value: object) -> bool:
    """Indica si un valor representa una cantidad entera mayor o igual a uno."""
    if isinstance(value, bool):
        return False

    return isinstance(value, int) and value >= 1


def is_valid_variation_mode(value: object) -> bool:
    """Valida los identificadores internos permitidos para variación de tiempo."""
    return isinstance(value, str) and value in VALID_VARIATION_MODES


def is_valid_execution_mode(value: object) -> bool:
    """Valida los modos declarativos permitidos para futuras ejecuciones."""
    return isinstance(value, str) and value in VALID_EXECUTION_MODES


def is_valid_key_selection_mode(value: object) -> bool:
    """Valida el modo usado por la UI para seleccionar teclas."""
    return isinstance(value, str) and value in VALID_KEY_SELECTION_MODES


def validate_action_key(key: object) -> bool:
    """Valida el campo ``key`` de una acción básica de macro."""
    return validate_key(key)


def validate_macro_action(action: object) -> bool:
    """Valida una acción de teclado básica guardable en JSON.

    La acción válida requiere una tecla soportada, un retardo base no negativo y
    un modo de variación conocido. Esta función solo revisa estructura de datos:
    no presiona teclas, no captura eventos y no interactúa con mouse.
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


def validate_action_data(action: object) -> bool:
    """Alias compatible con Fase 3 para validar una acción de macro."""
    return validate_macro_action(action)


def validate_macro_data(macro_data: object) -> bool:
    """Valida la estructura mínima de una macro completa de Fase 4.

    La validación es intencionalmente básica y estricta en los campos requeridos:
    confirma que la macro pueda guardarse, cargarse, importarse o exportarse como
    JSON del proyecto. No valida reglas de ejecución porque Fase 4 no ejecuta
    macros.
    """
    if not isinstance(macro_data, Mapping):
        return False

    if not REQUIRED_MACRO_FIELDS.issubset(macro_data):
        return False

    actions = macro_data["actions"]
    if not isinstance(actions, list):
        return False

    # Una macro ejecutable necesita al menos una acción. Aceptar listas vacías
    # crearía previews y runs engañosos que no representan una macro real.
    if not actions:
        return False

    if not all(validate_macro_action(action) for action in actions):
        return False

    infinite = macro_data["infinite"]
    if not isinstance(infinite, bool):
        return False

    if not infinite and not is_positive_integer(macro_data["repetitions"]):
        return False

    return (
        is_non_negative_number(macro_data["initial_delay"])
        and is_non_negative_number(macro_data["cooldown_base"])
        and is_valid_variation_mode(macro_data["cooldown_variation"])
        and is_valid_execution_mode(macro_data["execution_mode"])
        and is_valid_key_selection_mode(macro_data["key_selection_mode"])
    )
