"""Definiciones iniciales para el futuro ejecutor de macros.

En Fase 1 no se ejecutan teclas. Este módulo solo centraliza nombres de modos
permitidos para que el resto del proyecto use valores consistentes desde el
principio.
"""

EXECUTION_MODE_REAL = "real"
EXECUTION_MODE_TEST_LOG_ONLY = "test_log_only"
EXECUTION_MODE_TEST_KEYS_AND_LOG = "test_keys_and_log"

EXECUTION_MODE_LABELS = {
    EXECUTION_MODE_REAL: "Ejecución real",
    EXECUTION_MODE_TEST_LOG_ONLY: "Modo prueba: solo log",
    EXECUTION_MODE_TEST_KEYS_AND_LOG: "Modo prueba: teclas + log",
}


def get_execution_mode_label(mode: str) -> str:
    """Devuelve el texto visible de un modo de ejecución conocido."""
    return EXECUTION_MODE_LABELS.get(mode, "Modo de ejecución desconocido")
