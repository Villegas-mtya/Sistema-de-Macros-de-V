"""Pruebas de regresión y seguridad para MacroRunner."""

from __future__ import annotations

import copy
import unittest
from typing import Any

from app.key_mapper import map_key
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


class FakeKeyboardDevice:
    """Dispositivo falso que registra llamadas sin tocar el teclado real."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.pressed_keys: list[Any] = []
        self.released_keys: list[Any] = []

    def press(self, key: Any) -> None:
        self.calls.append(("press", key))
        self.pressed_keys.append(key)

    def release(self, key: Any) -> None:
        self.calls.append(("release", key))
        self.released_keys.append(key)


def event_types(events: list[dict[str, object]]) -> list[str]:
    """Extrae tipos de evento para hacer aserciones legibles."""
    return [str(event["type"]) for event in events]


class MacroRunnerTests(unittest.TestCase):
    """Garantiza test_log seguro y real testeable con dispositivo falso."""

    def test_test_log_runner_generates_start_and_finish_events(self) -> None:
        runner = MacroRunner(copy.deepcopy(BASE_MACRO), sleep_function=lambda seconds: None)

        events = runner.run()
        types = event_types(events)

        self.assertGreater(len(events), 0)
        self.assertIn("macro_started", types)
        self.assertIn("macro_finished", types)

    def test_test_log_does_not_create_keyboard_controller(self) -> None:
        def fail_if_controller_is_created() -> FakeKeyboardDevice:
            raise AssertionError("test_log no debe crear controlador real")

        runner = MacroRunner(
            copy.deepcopy(BASE_MACRO),
            sleep_function=lambda seconds: None,
            keyboard_controller_factory=fail_if_controller_is_created,
        )

        events = runner.run()

        self.assertIn("action", event_types(events))
        self.assertNotIn("real_key_pressed", event_types(events))

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

    def test_real_execution_uses_fake_controller_and_logs_expected_events(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["execution_mode"] = "real"
        fake_controller = FakeKeyboardDevice()
        runner = MacroRunner(
            macro,
            sleep_function=lambda seconds: None,
            keyboard_controller_factory=lambda: fake_controller,
        )

        events = runner.run()
        types = event_types(events)

        self.assertEqual([("press", fake_controller.calls[0][1]), ("release", fake_controller.calls[1][1])], fake_controller.calls)
        self.assertIn("real_execution_started", types)
        self.assertIn("real_key_pressed", types)
        self.assertIn("real_action_completed", types)
        self.assertIn("macro_finished", types)

    def test_real_execution_maps_character_and_special_keys(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["execution_mode"] = "real"
        macro["actions"] = [
            {"key": "a", "base_delay": 0.0, "variation_mode": "fixed"},
            {"key": "enter", "base_delay": 0.0, "variation_mode": "fixed"},
        ]
        fake_controller = FakeKeyboardDevice()
        runner = MacroRunner(
            macro,
            sleep_function=lambda seconds: None,
            keyboard_controller_factory=lambda: fake_controller,
        )

        runner.run()

        self.assertEqual(["a", map_key("enter")], fake_controller.pressed_keys)
        self.assertEqual(fake_controller.pressed_keys, fake_controller.released_keys)

    def test_real_execution_can_stop_before_first_action(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["execution_mode"] = "real"
        fake_controller = FakeKeyboardDevice()
        runner = MacroRunner(
            macro,
            stop_callback=lambda: True,
            sleep_function=lambda seconds: None,
            keyboard_controller_factory=lambda: fake_controller,
        )

        events = runner.run()

        self.assertEqual([], fake_controller.calls)
        self.assertIn("macro_stopped", event_types(events))

    def test_real_execution_can_stop_during_action_delay(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["execution_mode"] = "real"
        macro["actions"][0]["base_delay"] = 1.0
        fake_controller = FakeKeyboardDevice()
        runner_holder: dict[str, MacroRunner] = {}

        def stop_during_delay(_seconds: float) -> None:
            runner_holder["runner"].stop()

        runner = MacroRunner(
            macro,
            sleep_function=stop_during_delay,
            stop_check_interval=0.01,
            keyboard_controller_factory=lambda: fake_controller,
        )
        runner_holder["runner"] = runner

        events = runner.run()

        self.assertEqual("press", fake_controller.calls[0][0])
        self.assertEqual("release", fake_controller.calls[1][0])
        self.assertIn("macro_stopped", event_types(events))

    def test_test_keys_execution_mode_is_rejected(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["execution_mode"] = "test_keys"
        runner = MacroRunner(macro, sleep_function=lambda seconds: None)

        with self.assertRaises(ValueError):
            runner.run()

    def test_unknown_execution_mode_is_rejected(self) -> None:
        macro = copy.deepcopy(BASE_MACRO)
        macro["execution_mode"] = "unknown"
        runner = MacroRunner(macro, sleep_function=lambda seconds: None)

        with self.assertRaises(ValueError):
            runner.run()


if __name__ == "__main__":
    unittest.main()
