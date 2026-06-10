"""Pruebas de regresión para previsualización declarativa."""

from __future__ import annotations

import copy
import unittest

from app.preview import build_macro_preview


BASE_MACRO = {
    "app": "Sistema de Macros de V",
    "version": "1.0",
    "actions": [
        {"key": "enter", "base_delay": 1.0, "variation_mode": "fixed"},
        {"key": "up", "base_delay": 2.0, "variation_mode": "light"},
    ],
    "initial_delay": 0.5,
    "repetitions": 2,
    "infinite": False,
    "cooldown_base": 3.0,
    "cooldown_variation": "fixed",
    "execution_mode": "test_log",
    "key_selection_mode": "simple",
}


class PreviewTests(unittest.TestCase):
    """Comprueba conteos, nombres legibles y duración segura de macros."""

    def test_build_macro_preview_with_two_actions(self) -> None:
        preview = build_macro_preview(copy.deepcopy(BASE_MACRO))

        self.assertEqual(preview["actions_count"], 2)
        self.assertEqual(preview["actions"][0]["key_display_name"], "Enter")
        self.assertEqual(preview["actions"][1]["key_display_name"], "Flecha arriba")
        self.assertFalse(preview["duration_estimate"]["infinite"])
        self.assertIsNotNone(preview["duration_estimate"]["total"])

    def test_build_macro_preview_with_infinite_macro(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["infinite"] = True

        preview = build_macro_preview(macro)

        self.assertTrue(preview["duration_estimate"]["infinite"])
        self.assertIsNone(preview["duration_estimate"]["total"])
        self.assertIsNotNone(preview["duration_estimate"]["per_cycle"])


if __name__ == "__main__":
    unittest.main()
