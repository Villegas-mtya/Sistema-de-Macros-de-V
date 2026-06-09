"""Estructura base de macros para Sistema de Macros de V.

El guardado e importación con diálogos se implementará después. En esta fase se
mantiene una macro por defecto para documentar el formato oficial desde código.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app import APP_NAME, APP_VERSION
from app.macro_runner import EXECUTION_MODE_TEST_LOG_ONLY

DEFAULT_MACRO_DATA: dict[str, Any] = {
    "app": APP_NAME,
    "version": APP_VERSION,
    "actions": [],
    "initial_delay": 0.0,
    "repetitions": 1,
    "infinite": False,
    "cooldown_base": 0.0,
    "cooldown_variation": "fixed",
    "execution_mode": EXECUTION_MODE_TEST_LOG_ONLY,
    "key_selection_mode": "simple",
}


def get_default_macro_data() -> dict[str, Any]:
    """Devuelve una copia independiente de la macro inicial segura."""
    return deepcopy(DEFAULT_MACRO_DATA)
