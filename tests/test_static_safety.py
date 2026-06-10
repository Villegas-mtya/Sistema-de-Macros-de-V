"""Pruebas estáticas para impedir llamadas reales de teclado en archivos críticos."""

from __future__ import annotations

import unittest
from pathlib import Path


CRITICAL_FILES = [
    Path("app/ui.py"),
    Path("app/macro_runner.py"),
]
FORBIDDEN_SNIPPETS = ["Controller(", ".press(", ".release("]


class StaticSafetyTests(unittest.TestCase):
    """Busca patrones peligrosos sin abrir UI ni depender de un servidor gráfico."""

    def test_critical_files_do_not_call_real_keyboard_actions(self) -> None:
        combined_text = "".join(path.read_text(encoding="utf-8") for path in CRITICAL_FILES)

        for forbidden_snippet in FORBIDDEN_SNIPPETS:
            with self.subTest(forbidden_snippet=forbidden_snippet):
                self.assertNotIn(forbidden_snippet, combined_text)


if __name__ == "__main__":
    unittest.main()
