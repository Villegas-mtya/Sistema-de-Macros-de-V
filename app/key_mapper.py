"""Mapeo y normalización de teclas para macros manuales.

La Fase 3 centraliza aquí todo el conocimiento sobre teclas soportadas. La
interfaz puede mostrar etiquetas legibles, mientras que los archivos JSON deben
usar valores internos simples y estables como ``"enter"``, ``"up"`` o ``"a"``.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Any

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

SPECIAL_KEY_VALUES_BY_DISPLAY_NAME = {
    "Enter": "enter",
    "Space": "space",
    "Esc": "esc",
    "Tab": "tab",
    "Shift": "shift",
    "Ctrl": "ctrl",
    "Alt": "alt",
    "Flecha arriba": "up",
    "Flecha abajo": "down",
    "Flecha izquierda": "left",
    "Flecha derecha": "right",
}

SPECIAL_KEY_DISPLAY_NAMES_BY_VALUE = {
    key_value: display_name
    for display_name, key_value in SPECIAL_KEY_VALUES_BY_DISPLAY_NAME.items()
}

# Alias aceptados en modo avanzado. Las claves se comparan en minúsculas y sin
# espacios extremos para tolerar entradas manuales comunes sin aceptar textos
# ambiguos o demasiado largos.
ADVANCED_KEY_ALIASES = {
    "enter": "enter",
    "return": "enter",
    "space": "space",
    "spacebar": "space",
    " ": "space",
    "esc": "esc",
    "escape": "esc",
    "tab": "tab",
    "shift": "shift",
    "ctrl": "ctrl",
    "control": "ctrl",
    "alt": "alt",
    "up": "up",
    "arrow up": "up",
    "arrowup": "up",
    "flecha arriba": "up",
    "down": "down",
    "arrow down": "down",
    "arrowdown": "down",
    "flecha abajo": "down",
    "left": "left",
    "arrow left": "left",
    "arrowleft": "left",
    "flecha izquierda": "left",
    "right": "right",
    "arrow right": "right",
    "arrowright": "right",
    "flecha derecha": "right",
}

SPECIAL_PYNPUT_KEY_NAMES_BY_VALUE = {
    "enter": "enter",
    "space": "space",
    "esc": "esc",
    "tab": "tab",
    "shift": "shift",
    "ctrl": "ctrl",
    "alt": "alt",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    **{f"f{number}": f"f{number}" for number in range(1, 13)},
}

VALID_INTERNAL_KEY_VALUES = {
    *SPECIAL_KEY_DISPLAY_NAMES_BY_VALUE,
    *[f"f{number}" for number in range(1, 13)],
    *[chr(code) for code in range(ord("a"), ord("z") + 1)],
    *[str(number) for number in range(10)],
}


class _HeadlessPynputKey(Enum):
    """Representación mínima para entornos Linux sin servidor gráfico.

    ``pynput.keyboard.Key`` puede fallar al importarse en CI o contenedores sin
    ``DISPLAY``. La aplicación real en Windows seguirá devolviendo las constantes
    de pynput; este enum solo permite validar y probar el mapeo en entornos
    headless sin ejecutar teclas reales.
    """

    enter = "enter"
    space = "space"
    esc = "esc"
    tab = "tab"
    shift = "shift"
    ctrl = "ctrl"
    alt = "alt"
    up = "up"
    down = "down"
    left = "left"
    right = "right"
    f1 = "f1"
    f2 = "f2"
    f3 = "f3"
    f4 = "f4"
    f5 = "f5"
    f6 = "f6"
    f7 = "f7"
    f8 = "f8"
    f9 = "f9"
    f10 = "f10"
    f11 = "f11"
    f12 = "f12"

    def __str__(self) -> str:
        return f"Key.{self.value}"


def get_simple_key_options() -> list[str]:
    """Devuelve las teclas visibles disponibles para el modo simple.

    El orden es estable para que la UI muestre primero teclas especiales, luego
    teclas de función, letras y finalmente números.
    """
    return [
        *SPECIAL_KEY_LABELS,
        *FUNCTION_KEY_LABELS,
        *LETTER_KEY_LABELS,
        *NUMBER_KEY_LABELS,
    ]


def normalize_key(label_or_text: object) -> str | None:
    """Convierte una etiqueta visible o entrada manual a valor interno JSON.

    Devuelve ``None`` cuando la entrada no corresponde a una tecla soportada. No
    lanza excepciones para entradas inválidas porque esta función es usada por
    validadores y por futuros campos de texto de la UI.
    """
    if not isinstance(label_or_text, str):
        return None

    if label_or_text == " ":
        return "space"

    clean_text = label_or_text.strip()
    if not clean_text:
        return None

    lowered_text = clean_text.lower()

    if lowered_text in ADVANCED_KEY_ALIASES:
        return ADVANCED_KEY_ALIASES[lowered_text]

    if len(lowered_text) == 1:
        if "a" <= lowered_text <= "z" or "0" <= lowered_text <= "9":
            return lowered_text
        return None

    if lowered_text.startswith("f"):
        number_text = lowered_text[1:]
        if number_text.isdigit() and 1 <= int(number_text) <= 12:
            return lowered_text

    return None


def map_key(label_or_text: object) -> Any | None:
    """Devuelve el valor que debe recibir pynput para presionar una tecla.

    Las teclas especiales y F1-F12 se devuelven como ``pynput.keyboard.Key`` en
    entornos con backend disponible. Letras y números se devuelven como caracteres
    normales, que es el formato esperado por pynput para esas teclas.
    """
    normalized_key = normalize_key(label_or_text)
    if normalized_key is None:
        return None

    if _is_character_key(normalized_key):
        return normalized_key

    pynput_key_name = SPECIAL_PYNPUT_KEY_NAMES_BY_VALUE.get(normalized_key)
    if pynput_key_name is None:
        return None

    if _is_linux_headless_environment():
        return getattr(_HeadlessPynputKey, pynput_key_name)

    from pynput.keyboard import Key

    return getattr(Key, pynput_key_name)


def validate_key(label_or_text: object) -> bool:
    """Indica si una etiqueta o entrada manual representa una tecla soportada."""
    normalized_key = normalize_key(label_or_text)
    return normalized_key in VALID_INTERNAL_KEY_VALUES


def get_key_display_name(key_value: object) -> str | None:
    """Convierte un valor interno normalizado en un nombre legible para la UI."""
    normalized_key = normalize_key(key_value)
    if normalized_key is None:
        return None

    if normalized_key in SPECIAL_KEY_DISPLAY_NAMES_BY_VALUE:
        return SPECIAL_KEY_DISPLAY_NAMES_BY_VALUE[normalized_key]

    if normalized_key.startswith("f") and normalized_key[1:].isdigit():
        return normalized_key.upper()

    if _is_character_key(normalized_key):
        return normalized_key.upper() if normalized_key.isalpha() else normalized_key

    return None


def _is_character_key(key_value: str) -> bool:
    """Reconoce letras y números que pynput recibe como caracteres simples."""
    return len(key_value) == 1 and (
        "a" <= key_value <= "z" or "0" <= key_value <= "9"
    )


def _is_linux_headless_environment() -> bool:
    """Evita importar pynput cuando Linux no tiene servidor gráfico disponible."""
    return (
        os.name == "posix"
        and not os.environ.get("DISPLAY")
        and not os.environ.get("WAYLAND_DISPLAY")
    )


__all__ = [
    "get_simple_key_options",
    "normalize_key",
    "map_key",
    "validate_key",
    "get_key_display_name",
]
