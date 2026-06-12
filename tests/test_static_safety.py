"""Pruebas estáticas para acotar la ejecución real de teclado de Fase 22."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


AUTHORIZED_KEYBOARD_FILE = Path("app/macro_runner.py")
UI_FILE = Path("app/ui.py")
FORBIDDEN_KEYBOARD_SNIPPETS = ["Control" + "ler", "." + "press(", "." + "release("]
FORBIDDEN_MODULE_NAMES = {
    "recorder.py",
    "macro_recorder.py",
    "keyboard_recorder.py",
    "player.py",
    "duration.py",
    "mouse.py",
    "mouse_controller.py",
    "clicker.py",
    "clicks.py",
    "mover.py",
    "movement.py",
    "movements.py",
}
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "build",
    "dist",
}


def iter_versioned_project_files() -> list[Path]:
    """Devuelve solo archivos versionados para evitar dependencias y artefactos.

    La prueba usa ``git ls-files`` como fuente de verdad del repositorio. Así no
    escanea paquetes instalados en ``.venv/``, caches, builds ni archivos locales
    no versionados que pueden contener llamadas legítimas de terceros.
    """
    completed_process = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )

    versioned_files = []
    for raw_path in completed_process.stdout.splitlines():
        path = Path(raw_path)
        if path.suffix == ".pyc":
            continue
        if EXCLUDED_PARTS.intersection(path.parts):
            continue
        versioned_files.append(path)

    return versioned_files


def iter_versioned_python_files() -> list[Path]:
    """Lista archivos Python propios y versionados del proyecto."""
    return [path for path in iter_versioned_project_files() if path.suffix == ".py"]


class StaticSafetyTests(unittest.TestCase):
    """Busca patrones peligrosos sin abrir UI ni depender de un servidor gráfico."""

    def test_keyboard_controller_calls_are_limited_to_macro_runner(self) -> None:
        for path in iter_versioned_python_files():
            text = path.read_text(encoding="utf-8")
            for forbidden_snippet in FORBIDDEN_KEYBOARD_SNIPPETS:
                with self.subTest(path=str(path), forbidden_snippet=forbidden_snippet):
                    if path == AUTHORIZED_KEYBOARD_FILE:
                        continue
                    self.assertNotIn(forbidden_snippet, text)

    def test_ui_does_not_call_keyboard_controller_directly(self) -> None:
        ui_text = UI_FILE.read_text(encoding="utf-8")
        for forbidden_snippet in FORBIDDEN_KEYBOARD_SNIPPETS:
            with self.subTest(forbidden_snippet=forbidden_snippet):
                self.assertNotIn(forbidden_snippet, ui_text)

    def test_no_new_recorder_mouse_click_or_movement_modules_exist(self) -> None:
        project_files = {path.name for path in iter_versioned_project_files()}
        forbidden_found = sorted(project_files & FORBIDDEN_MODULE_NAMES)
        self.assertEqual([], forbidden_found)


if __name__ == "__main__":
    unittest.main()
