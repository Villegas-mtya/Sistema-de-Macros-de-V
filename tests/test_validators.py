"""Pruebas de regresión para validadores de macros."""

from __future__ import annotations

import copy
import unittest

from app.validators import validate_macro_action, validate_macro_data


VALID_ACTION = {
    "key": "enter",
    "base_delay": 0.0,
    "variation_mode": "fixed",
}

VALID_MACRO = {
    "app": "Sistema de Macros de V",
    "version": "1.0",
    "actions": [VALID_ACTION],
    "initial_delay": 0.0,
    "repetitions": 1,
    "infinite": False,
    "cooldown_base": 0.0,
    "cooldown_variation": "fixed",
    "execution_mode": "test_log",
    "key_selection_mode": "simple",
}


class ValidatorsTests(unittest.TestCase):
    """Protege la estructura mínima de acciones y macros JSON."""

    def test_valid_macro_with_test_log_execution_mode(self) -> None:
        self.assertTrue(validate_macro_data(copy.deepcopy(VALID_MACRO)))

    def test_valid_action(self) -> None:
        self.assertTrue(validate_macro_action(copy.deepcopy(VALID_ACTION)))

    def test_valid_macro_with_real_execution_mode(self) -> None:
        macro = copy.deepcopy(VALID_MACRO)
        macro["execution_mode"] = "real"
        self.assertTrue(validate_macro_data(macro))

    def test_reject_test_keys_execution_mode(self) -> None:
        macro = copy.deepcopy(VALID_MACRO)
        macro["execution_mode"] = "test_keys"
        self.assertFalse(validate_macro_data(macro))

    def test_reject_unknown_execution_mode(self) -> None:
        macro = copy.deepcopy(VALID_MACRO)
        macro["execution_mode"] = "modo_desconocido"
        self.assertFalse(validate_macro_data(macro))

    def test_reject_empty_execution_mode(self) -> None:
        macro = copy.deepcopy(VALID_MACRO)
        macro["execution_mode"] = ""
        self.assertFalse(validate_macro_data(macro))

    def test_reject_none_execution_mode(self) -> None:
        macro = copy.deepcopy(VALID_MACRO)
        macro["execution_mode"] = None
        self.assertFalse(validate_macro_data(macro))

    def test_reject_macro_without_actions(self) -> None:
        macro = copy.deepcopy(VALID_MACRO)
        macro["actions"] = []
        self.assertFalse(validate_macro_data(macro))

    def test_reject_invalid_key(self) -> None:
        macro = copy.deepcopy(VALID_MACRO)
        macro["actions"][0]["key"] = "tecla_invalida"
        self.assertFalse(validate_macro_data(macro))

    def test_reject_invalid_variation_mode(self) -> None:
        macro = copy.deepcopy(VALID_MACRO)
        macro["actions"][0]["variation_mode"] = "variacion_invalida"
        self.assertFalse(validate_macro_data(macro))


if __name__ == "__main__":
    unittest.main()
