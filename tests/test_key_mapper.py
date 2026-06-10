"""Pruebas de regresión para el mapeo seguro de teclas."""

from __future__ import annotations

import unittest

from app.key_mapper import get_key_display_name, normalize_key, validate_key


class KeyMapperTests(unittest.TestCase):
    """Valida normalización, aceptación y visualización de teclas soportadas."""

    def test_normalize_known_special_keys(self) -> None:
        self.assertEqual(normalize_key("Enter"), "enter")
        self.assertEqual(normalize_key("Flecha arriba"), "up")

    def test_validate_function_key_and_reject_unknown_key(self) -> None:
        self.assertTrue(validate_key("F12"))
        self.assertFalse(validate_key("tecla_invalida"))

    def test_get_key_display_name_for_internal_value(self) -> None:
        self.assertEqual(get_key_display_name("enter"), "Enter")


if __name__ == "__main__":
    unittest.main()
