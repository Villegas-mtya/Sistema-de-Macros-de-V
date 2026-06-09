"""Opciones iniciales de teclas para el constructor manual de macros."""

from __future__ import annotations

SPECIAL_KEY_LABELS = [
    "Enter",
    "Space",
    "Esc",
    "Tab",
    "Shift",
    "Ctrl",
    "Alt",
    "Flecha arriba",
    "Flecha abajo",
    "Flecha izquierda",
    "Flecha derecha",
]
FUNCTION_KEY_LABELS = [f"F{number}" for number in range(1, 13)]
LETTER_KEY_LABELS = [chr(code) for code in range(ord("A"), ord("Z") + 1)]
NUMBER_KEY_LABELS = [str(number) for number in range(10)]


def get_simple_key_options() -> list[str]:
    """Devuelve las teclas disponibles para el modo simple."""
    return [
        *SPECIAL_KEY_LABELS,
        *FUNCTION_KEY_LABELS,
        *LETTER_KEY_LABELS,
        *NUMBER_KEY_LABELS,
    ]
