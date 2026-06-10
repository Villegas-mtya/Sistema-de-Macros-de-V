"""Pruebas de regresión y seguridad para MacroRunner."""

from __future__ import annotations

import copy
import unittest

from app.macro_runner import MacroRunner


BASE_MACRO = {
    "app": "Sistema de Macros de V",
    "version": "1.0",
    "actions": [
        {"key": "enter", "base_delay": 0.0, "variation_mode": "fixed"},
    ],
    "initial_delay": 0.0,
    "repetitions": 1,
    "infinite": False,
    "cooldown_base": 0.0,
    "cooldown_variation": "fixed",
    "execution_mode": "test_log",
    "key_selection_mode": "simple",
}


def event_types(events: list[dict[str, object]]) -> list[str]:
    """Extrae tipos de evento para hacer aserciones legibles."""
    return [str(event["type"]) for event in events]


class MacroRunnerTests(unittest.TestCase):
    """Garantiza que el runner solo simule logs y rechace modos peligrosos."""

    def test_test_log_runner_generates_start_and_finish_events(self) -> None:
        runner = MacroRunner(copy.deepcopy(BASE_MACRO), sleep_function=lambda seconds: None)

        events = runner.run()
        types = event_types(events)

        self.assertGreater(len(events), 0)
        self.assertIn("macro_started", types)
        self.assertIn("macro_finished", types)

    def test_runner_stop_finishes_as_macro_stopped(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["initial_delay"] = 1.0
        runner_holder: dict[str, MacroRunner] = {}

        def stop_during_first_sleep(_seconds: float) -> None:
            runner_holder["runner"].stop()

        runner = MacroRunner(
            macro,
            sleep_function=stop_during_first_sleep,
            stop_check_interval=0.01,
        )
        runner_holder["runner"] = runner

        events = runner.run()

        self.assertIn("macro_stopped", event_types(events))

    def test_real_execution_mode_is_rejected(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["execution_mode"] = "real"
        runner = MacroRunner(macro, sleep_function=lambda seconds: None)

        with self.assertRaises(ValueError):
            runner.run()

    def test_test_keys_execution_mode_is_rejected(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["execution_mode"] = "test_keys"
        runner = MacroRunner(macro, sleep_function=lambda seconds: None)

        with self.assertRaises(ValueError):
            runner.run()


if __name__ == "__main__":
    unittest.main()
