"""Runner de macros en modo prueba solo log.

La Fase 6 agrega un ejecutor seguro para recorrer macros validadas sin pulsar
teclas reales. El runner respeta retardos, variaciones, repeticiones y cooldown,
pero solo emite eventos de log en memoria o hacia un callback externo.

Límites deliberados de esta fase:
- No usa ``pynput.Controller``.
- No presiona teclas reales.
- No registra listeners globales.
- No implementa F9 global ni botón operativo ``Detener ahora``.
"""

from __future__ import annotations

import random
import threading
import time
from collections.abc import Callable
from typing import Any

from app.key_mapper import get_key_display_name
from app.validators import validate_macro_data

EXECUTION_MODE_REAL = "real"
EXECUTION_MODE_TEST_LOG = "test_log"
EXECUTION_MODE_TEST_KEYS = "test_keys"

# Alias heredados de la base inicial. Se mantienen para no romper imports
# externos, pero la Fase 6 solo permite EXECUTION_MODE_TEST_LOG.
EXECUTION_MODE_TEST_LOG_ONLY = EXECUTION_MODE_TEST_LOG
EXECUTION_MODE_TEST_KEYS_AND_LOG = EXECUTION_MODE_TEST_KEYS

EXECUTION_MODE_LABELS = {
    EXECUTION_MODE_REAL: "Ejecución real",
    EXECUTION_MODE_TEST_LOG: "Modo prueba: solo log",
    EXECUTION_MODE_TEST_KEYS: "Modo prueba: teclas + log",
}

VARIATION_SECONDS = {
    "fixed": 0.0,
    "light": 0.15,
    "medium": 0.30,
    "high": 0.50,
}

RunnerEvent = dict[str, Any]
LogCallback = Callable[[RunnerEvent], None]
StopCallback = Callable[[], bool]
SleepFunction = Callable[[float], None]


class MacroRunner:
    """Ejecuta una simulación segura de macro y registra eventos legibles.

    ``MacroRunner`` es intencionalmente pequeño y síncrono en ``run()`` para que
    sea fácil de probar. Si una UI futura necesita no bloquear su hilo principal,
    puede llamar a ``start()`` y luego solicitar detención con ``stop()``.
    """

    def __init__(
        self,
        macro_data: object,
        log_callback: LogCallback | None = None,
        stop_callback: StopCallback | None = None,
        sleep_function: SleepFunction | None = None,
    ) -> None:
        self.macro_data = macro_data
        self.log_callback = log_callback
        self.stop_callback = stop_callback
        self.sleep_function = sleep_function or time.sleep
        self.events: list[RunnerEvent] = []
        self._stop_requested = False
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        """Indica si el runner lanzado con ``start()`` sigue activo."""
        return self._thread is not None and self._thread.is_alive()

    @property
    def stop_requested(self) -> bool:
        """Indica si se solicitó detención por ``stop()`` o ``stop_callback``."""
        return self._should_stop()

    def stop(self) -> None:
        """Solicita detener la simulación en el siguiente punto seguro.

        Esta función no instala F9 global ni opera botones visuales. Solo cambia
        una bandera interna que ``run()`` revisa antes de cada bloque importante.
        """
        self._stop_requested = True

    def start(self) -> threading.Thread:
        """Inicia ``run()`` en un hilo daemon para no bloquear una UI futura."""
        if self.is_running:
            raise RuntimeError("La macro ya se está ejecutando")

        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        return self._thread

    def run(self) -> list[RunnerEvent]:
        """Recorre la macro validada en modo ``test_log`` y devuelve eventos.

        El algoritmo es deliberadamente narrativo:
        1. Validar la estructura y el modo de ejecución.
        2. Registrar inicio y esperar el delay inicial.
        3. Recorrer repeticiones finitas o infinitas.
        4. Simular cada acción como texto, sin emitir teclas reales.
        5. Aplicar cooldown entre repeticiones.
        6. Finalizar correctamente o detenerse si se pidió stop.
        """
        try:
            self._validate_before_run()
            macro = self.macro_data
            assert isinstance(macro, dict)

            self._emit(
                "macro_started",
                "Iniciando macro en modo prueba: solo log",
                {
                    "execution_mode": macro["execution_mode"],
                    "infinite": macro["infinite"],
                    "repetitions": macro["repetitions"],
                    "actions_count": len(macro["actions"]),
                },
            )

            if self._stop_if_requested("Detención solicitada antes del delay inicial"):
                return self.events

            self._sleep_and_log_delay(
                event_type="initial_delay",
                message="Esperando delay inicial",
                delay_seconds=float(macro["initial_delay"]),
                data={"field": "initial_delay"},
            )

            repetition_number = 1
            while macro["infinite"] or repetition_number <= macro["repetitions"]:
                if self._stop_if_requested(
                    "Detención solicitada antes de iniciar la repetición",
                    {"repetition": repetition_number},
                ):
                    return self.events

                self._emit(
                    "repetition_started",
                    f"Iniciando repetición {repetition_number}",
                    {"repetition": repetition_number, "infinite": macro["infinite"]},
                )

                for action_index, action in enumerate(macro["actions"], start=1):
                    if self._stop_if_requested(
                        "Detención solicitada antes de ejecutar la acción simulada",
                        {"repetition": repetition_number, "action_index": action_index},
                    ):
                        return self.events

                    self._simulate_action(action, action_index, repetition_number)

                if self._must_run_cooldown(macro, repetition_number):
                    if self._stop_if_requested(
                        "Detención solicitada antes del cooldown",
                        {"repetition": repetition_number},
                    ):
                        return self.events

                    cooldown_delay = get_randomized_delay(
                        macro["cooldown_base"], macro["cooldown_variation"]
                    )
                    self._sleep_and_log_delay(
                        event_type="cooldown",
                        message="Esperando cooldown entre repeticiones",
                        delay_seconds=cooldown_delay,
                        data={
                            "repetition": repetition_number,
                            "base_delay": float(macro["cooldown_base"]),
                            "variation_mode": macro["cooldown_variation"],
                        },
                    )

                repetition_number += 1

            self._emit("macro_finished", "Macro finalizada correctamente")
            return self.events
        except ValueError as error:
            self._emit(
                "validation_error",
                str(error),
                {"error_type": type(error).__name__},
            )
            raise

    def _validate_before_run(self) -> None:
        """Valida estructura y bloquea modos no seguros para Fase 6."""
        if not validate_macro_data(self.macro_data):
            raise ValueError("La macro no cumple la estructura válida para ejecutarse")

        macro = self.macro_data
        assert isinstance(macro, dict)
        execution_mode = macro["execution_mode"]

        if execution_mode == EXECUTION_MODE_TEST_LOG:
            return

        if execution_mode == EXECUTION_MODE_REAL:
            raise ValueError(
                "El modo real todavía no está permitido: falta F9 global y controles "
                "de emergencia antes de presionar teclas reales"
            )

        if execution_mode == EXECUTION_MODE_TEST_KEYS:
            raise ValueError(
                "El modo test_keys todavía no está permitido porque implicaría "
                "presionar teclas; Fase 6 solo registra logs"
            )

        raise ValueError(f"Modo de ejecución no soportado en Fase 6: {execution_mode!r}")

    def _simulate_action(
        self,
        action: dict[str, Any],
        action_index: int,
        repetition_number: int,
    ) -> None:
        """Registra una acción simulada y espera su delay aleatorizado."""
        key_display_name = get_key_display_name(action["key"]) or str(action["key"])
        self._emit(
            "action",
            f"Simulando tecla {key_display_name}",
            {
                "repetition": repetition_number,
                "action_index": action_index,
                "key": action["key"],
                "key_display_name": key_display_name,
            },
        )

        action_delay = get_randomized_delay(action["base_delay"], action["variation_mode"])
        self._sleep_and_log_delay(
            event_type="action_delay",
            message=f"Esperando delay de acción {action_index}",
            delay_seconds=action_delay,
            data={
                "repetition": repetition_number,
                "action_index": action_index,
                "base_delay": float(action["base_delay"]),
                "variation_mode": action["variation_mode"],
            },
        )

    def _sleep_and_log_delay(
        self,
        event_type: str,
        message: str,
        delay_seconds: float,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Emite el evento de espera y duerme de forma sustituible en pruebas."""
        event_data = dict(data or {})
        event_data["delay_seconds"] = delay_seconds
        self._emit(event_type, message, event_data)
        self._sleep_with_stop_checks(delay_seconds)

    def _sleep_with_stop_checks(self, seconds: float) -> None:
        """Duerme en tramos cortos para que ``stop()`` sea atendido pronto."""
        remaining_seconds = seconds
        while remaining_seconds > 0:
            if self._should_stop():
                return

            sleep_chunk = min(remaining_seconds, 0.1)
            self.sleep_function(sleep_chunk)
            remaining_seconds -= sleep_chunk

    def _must_run_cooldown(self, macro: dict[str, Any], repetition_number: int) -> bool:
        """Indica si corresponde cooldown después de una repetición."""
        if macro["infinite"]:
            return True

        return repetition_number < macro["repetitions"]

    def _should_stop(self) -> bool:
        """Centraliza la bandera interna y el callback externo opcional."""
        if self._stop_requested:
            return True

        if self.stop_callback is None:
            return False

        return bool(self.stop_callback())

    def _stop_if_requested(
        self,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> bool:
        """Registra la detención una sola vez cuando se alcanza un punto seguro."""
        if not self._should_stop():
            return False

        self._stop_requested = True
        self._emit("stop_requested", message, data)
        return True

    def _emit(
        self,
        event_type: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> RunnerEvent:
        """Crea, guarda y entrega un evento al callback opcional."""
        event = create_runner_event(event_type, message, data)
        self.events.append(event)

        if self.log_callback is not None:
            self.log_callback(event)

        return event


def get_execution_mode_label(mode: str) -> str:
    """Devuelve el texto visible de un modo de ejecución conocido."""
    return EXECUTION_MODE_LABELS.get(mode, "Modo de ejecución desconocido")


def get_randomized_delay(base_delay: object, variation_mode: str) -> float:
    """Devuelve un delay aleatorio seguro para el modo de variación recibido.

    La variación se aplica en segundos, no como porcentaje:
    ``fixed`` no modifica el valor, ``light`` varía ±0.15 s, ``medium`` ±0.30 s y
    ``high`` ±0.50 s. El mínimo nunca baja de cero.
    """
    delay = _to_non_negative_float(base_delay, "base_delay")
    variation = _get_variation_seconds(variation_mode)

    if variation == 0.0:
        return delay

    minimum_delay = max(0.0, delay - variation)
    maximum_delay = delay + variation
    return random.uniform(minimum_delay, maximum_delay)


def create_runner_event(
    event_type: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> RunnerEvent:
    """Crea un evento serializable y legible para logs o UI futura."""
    return {
        "type": event_type,
        "message": message,
        "data": data or {},
    }


def _get_variation_seconds(variation_mode: str) -> float:
    """Valida y devuelve la variación aprobada para Fase 6."""
    if variation_mode not in VARIATION_SECONDS:
        valid_modes = ", ".join(sorted(VARIATION_SECONDS))
        raise ValueError(
            f"Modo de variación inválido: {variation_mode!r}. "
            f"Modos válidos: {valid_modes}"
        )

    return VARIATION_SECONDS[variation_mode]


def _to_non_negative_float(value: object, field_name: str) -> float:
    """Convierte a float rechazando booleanos, textos inválidos y negativos."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} debe ser un número mayor o igual a cero")

    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{field_name} debe ser un número mayor o igual a cero"
        ) from error

    if numeric_value < 0:
        raise ValueError(f"{field_name} no puede ser negativo")

    return numeric_value


__all__ = [
    "EXECUTION_MODE_REAL",
    "EXECUTION_MODE_TEST_LOG",
    "EXECUTION_MODE_TEST_KEYS",
    "EXECUTION_MODE_TEST_LOG_ONLY",
    "EXECUTION_MODE_TEST_KEYS_AND_LOG",
    "EXECUTION_MODE_LABELS",
    "VARIATION_SECONDS",
    "MacroRunner",
    "get_execution_mode_label",
    "get_randomized_delay",
    "create_runner_event",
]
