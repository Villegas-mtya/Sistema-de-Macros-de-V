"""Runner de macros en modo prueba solo log con parada de emergencia.

La Fase 7 mantiene el ejecutor seguro de Fase 6 y agrega parada de emergencia
sin habilitar ejecución real de teclas. El runner respeta retardos,
variaciones, repeticiones y cooldown, pero solo emite eventos de log en memoria
o hacia un callback externo.

Límites deliberados de esta fase:
- No usa ``pynput.Controller``.
- No presiona teclas reales.
- No captura teclas para grabar acciones.
- La única escucha global permitida es F9 para solicitar detención.
- No implementa botón visual ``Detener ahora`` ni integración con ``app/ui.py``.
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
# externos, pero la Fase 7 solo permite EXECUTION_MODE_TEST_LOG.
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

DEFAULT_STOP_CHECK_INTERVAL = 0.1

RunnerEvent = dict[str, Any]
LogCallback = Callable[[RunnerEvent], None]
StopCallback = Callable[[], bool]
SleepFunction = Callable[[float], None]
EmergencyCallback = Callable[[dict[str, Any]], None]


class EmergencyStopController:
    """Control mínimo de parada de emergencia para Fase 7.

    La responsabilidad de esta clase es pequeña y explícita: recordar si se pidió
    una parada de emergencia, permitir dispararla desde pruebas sin teclado físico
    y, opcionalmente, iniciar un listener global que solo reacciona a F9. No guarda
    teclas, no registra entradas y no interpreta ninguna tecla distinta de F9.
    """

    def __init__(self, callback: EmergencyCallback | None = None) -> None:
        self._callbacks: list[EmergencyCallback] = []
        if callback is not None:
            self._callbacks.append(callback)

        self._triggered = False
        self._listener: Any | None = None
        self._lock = threading.Lock()

    @property
    def is_triggered(self) -> bool:
        """Indica si la parada de emergencia ya fue solicitada."""
        with self._lock:
            return self._triggered

    @property
    def is_listener_running(self) -> bool:
        """Indica si el listener global de F9 está activo."""
        listener = self._listener
        return listener is not None and bool(getattr(listener, "running", True))

    def add_callback(self, callback: EmergencyCallback) -> None:
        """Registra un callback que se llamará una sola vez al disparar stop."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def trigger(self, source: str = "manual") -> bool:
        """Dispara la parada de emergencia de forma testeable.

        Devuelve ``True`` solo la primera vez que cambia el estado. Llamadas
        posteriores mantienen la parada solicitada sin duplicar callbacks.
        """
        with self._lock:
            if self._triggered:
                return False

            self._triggered = True

        payload = {"source": source}
        for callback in tuple(self._callbacks):
            callback(payload)

        return True

    def request_emergency_stop(self, source: str = "manual") -> bool:
        """Alias legible para disparar la parada de emergencia."""
        return self.trigger(source=source)

    def start_listener(self) -> bool:
        """Inicia un listener global no bloqueante limitado exclusivamente a F9.

        Si ``pynput`` no está disponible o el entorno no permite listeners
        globales, esta función puede lanzar el error correspondiente al llamador.
        El runner no la activa por defecto para que las pruebas headless sigan
        siendo rápidas y deterministas.
        """
        if self._listener is not None:
            return False

        from pynput.keyboard import Key, Listener

        def on_press(key: object) -> bool | None:
            # La única tecla observada por Fase 7 es F9. Cualquier otra entrada se
            # ignora sin guardar datos, sin loguear la tecla y sin afectar acciones.
            if key == Key.f9:
                self.trigger(source="f9")
                return False

            return None

        self._listener = Listener(on_press=on_press)
        self._listener.start()
        return True

    def stop_listener(self) -> bool:
        """Detiene el listener global de F9 si está activo."""
        listener = self._listener
        if listener is None:
            return False

        listener.stop()
        self._listener = None
        return True


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
        emergency_stop_checker: StopCallback | None = None,
        emergency_stop_controller: EmergencyStopController | None = None,
        enable_emergency_listener: bool = False,
        stop_check_interval: float = DEFAULT_STOP_CHECK_INTERVAL,
    ) -> None:
        self.macro_data = macro_data
        self.log_callback = log_callback
        self.stop_callback = stop_callback
        self.sleep_function = sleep_function or time.sleep
        self.emergency_stop_checker = emergency_stop_checker
        controller_factory = EmergencyStopController
        self.emergency_stop_controller = (
            emergency_stop_controller or controller_factory()
        )
        self.enable_emergency_listener = enable_emergency_listener
        self.stop_check_interval = _to_positive_float(
            stop_check_interval,
            "stop_check_interval",
        )

        self.events: list[RunnerEvent] = []
        self._stop_requested = False
        self._emergency_stop_requested = False
        self._stop_event_logged = False
        self._emergency_event_logged = False
        self._thread: threading.Thread | None = None

        self.emergency_stop_controller.add_callback(self._handle_emergency_stop)

    @property
    def is_running(self) -> bool:
        """Indica si el runner lanzado con ``start()`` sigue activo."""
        return self._thread is not None and self._thread.is_alive()

    @property
    def stop_requested(self) -> bool:
        """Indica si se solicitó detención manual, externa o de emergencia."""
        return self._should_stop()

    @property
    def emergency_stop_requested(self) -> bool:
        """Indica si la parada de emergencia fue disparada."""
        self._sync_external_emergency_state()
        return self._emergency_stop_requested

    def stop(self) -> None:
        """Solicita detener la simulación en el siguiente punto seguro.

        Esta función no instala F9 global ni opera botones visuales. Solo cambia
        una bandera interna que ``run()`` revisa antes y durante bloques largos.
        """
        self._stop_requested = True

    def trigger_emergency_stop(self, source: str = "manual") -> bool:
        """Dispara una parada de emergencia sin requerir presionar F9 físicamente."""
        return self.emergency_stop_controller.trigger(source=source)

    def request_emergency_stop(self, source: str = "manual") -> bool:
        """Alias explícito para pruebas y futuras integraciones de UI."""
        return self.trigger_emergency_stop(source=source)

    def start_emergency_listener(self) -> bool:
        """Inicia el listener global de F9 y registra el evento correspondiente."""
        started = self.emergency_stop_controller.start_listener()
        if started:
            self._emit(
                "emergency_listener_started",
                "Listener global de emergencia F9 iniciado",
                {"key": "f9"},
            )

        return started

    def stop_emergency_listener(self) -> bool:
        """Detiene el listener global de F9 y registra el evento correspondiente."""
        stopped = self.emergency_stop_controller.stop_listener()
        if stopped:
            self._emit(
                "emergency_listener_stopped",
                "Listener global de emergencia F9 detenido",
                {"key": "f9"},
            )

        return stopped

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
        2. Iniciar opcionalmente el listener global F9, si fue solicitado.
        3. Registrar inicio y revisar detención antes del delay inicial.
        4. Dormir en tramos cortos para detectar stop durante delays largos.
        5. Recorrer repeticiones y acciones simuladas sin emitir teclas reales.
        6. Aplicar cooldown entre repeticiones.
        7. Finalizar correctamente o registrar parada segura.
        """
        listener_started_by_run = False

        try:
            self._validate_before_run()
            macro = self.macro_data
            assert isinstance(macro, dict)

            if self.enable_emergency_listener:
                listener_started_by_run = self.start_emergency_listener()

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
                return self._finish_stopped()

            if self._sleep_and_log_delay(
                event_type="initial_delay",
                message="Esperando delay inicial",
                delay_seconds=float(macro["initial_delay"]),
                data={"field": "initial_delay"},
            ):
                self._stop_if_requested("Detención solicitada durante el delay inicial")
                return self._finish_stopped()

            repetition_number = 1
            while macro["infinite"] or repetition_number <= macro["repetitions"]:
                if self._stop_if_requested(
                    "Detención solicitada antes de iniciar la repetición",
                    {"repetition": repetition_number},
                ):
                    return self._finish_stopped()

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
                        return self._finish_stopped()

                    if self._simulate_action(action, action_index, repetition_number):
                        self._stop_if_requested(
                            "Detención solicitada durante el delay de acción",
                            {
                                "repetition": repetition_number,
                                "action_index": action_index,
                            },
                        )
                        return self._finish_stopped()

                if self._must_run_cooldown(macro, repetition_number):
                    if self._stop_if_requested(
                        "Detención solicitada antes del cooldown",
                        {"repetition": repetition_number},
                    ):
                        return self._finish_stopped()

                    cooldown_delay = get_randomized_delay(
                        macro["cooldown_base"], macro["cooldown_variation"]
                    )
                    if self._sleep_and_log_delay(
                        event_type="cooldown",
                        message="Esperando cooldown entre repeticiones",
                        delay_seconds=cooldown_delay,
                        data={
                            "repetition": repetition_number,
                            "base_delay": float(macro["cooldown_base"]),
                            "variation_mode": macro["cooldown_variation"],
                        },
                    ):
                        self._stop_if_requested(
                            "Detención solicitada durante el cooldown",
                            {"repetition": repetition_number},
                        )
                        return self._finish_stopped()

                repetition_number += 1

            if self._stop_if_requested("Detención solicitada antes de finalizar"):
                return self._finish_stopped()

            self._emit("macro_finished", "Macro finalizada correctamente")
            return self.events
        except ValueError as error:
            self._emit(
                "validation_error",
                str(error),
                {"error_type": type(error).__name__},
            )
            raise
        finally:
            if listener_started_by_run:
                self.stop_emergency_listener()

    def _validate_before_run(self) -> None:
        """Valida estructura y bloquea modos no seguros para Fase 7."""
        if not validate_macro_data(self.macro_data):
            raise ValueError("La macro no cumple la estructura válida para ejecutarse")

        macro = self.macro_data
        assert isinstance(macro, dict)
        execution_mode = macro["execution_mode"]

        if execution_mode == EXECUTION_MODE_TEST_LOG:
            return

        if execution_mode == EXECUTION_MODE_REAL:
            raise ValueError(
                "El modo real todavía no está permitido: falta la ejecución segura "
                "con controles completos antes de presionar teclas reales"
            )

        if execution_mode == EXECUTION_MODE_TEST_KEYS:
            raise ValueError(
                "El modo test_keys todavía no está permitido porque implicaría "
                "presionar teclas; Fase 7 solo registra logs"
            )

        raise ValueError(f"Modo de ejecución no soportado en Fase 7: {execution_mode!r}")

    def _simulate_action(
        self,
        action: dict[str, Any],
        action_index: int,
        repetition_number: int,
    ) -> bool:
        """Registra una acción simulada y espera su delay aleatorizado.

        Devuelve ``True`` si el delay fue interrumpido por una solicitud de stop.
        """
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
        return self._sleep_and_log_delay(
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
    ) -> bool:
        """Emite el evento de espera y duerme de forma interrumpible.

        Devuelve ``True`` cuando el sleep se interrumpe por stop manual, parada de
        emergencia, callback externo o listener F9.
        """
        event_data = dict(data or {})
        event_data["delay_seconds"] = delay_seconds
        self._emit(event_type, message, event_data)
        return self._sleep_with_stop_checks(delay_seconds)

    def _sleep_with_stop_checks(self, seconds: float) -> bool:
        """Duerme en tramos cortos para que ``stop()`` y F9 se atiendan pronto."""
        remaining_seconds = seconds
        while remaining_seconds > 0:
            if self._should_stop():
                return True

            sleep_chunk = min(remaining_seconds, self.stop_check_interval)
            self.sleep_function(sleep_chunk)
            remaining_seconds -= sleep_chunk

        return self._should_stop()

    def _must_run_cooldown(self, macro: dict[str, Any], repetition_number: int) -> bool:
        """Indica si corresponde cooldown después de una repetición."""
        if macro["infinite"]:
            return True

        return repetition_number < macro["repetitions"]

    def _should_stop(self) -> bool:
        """Centraliza bandera interna, callbacks externos y emergencia."""
        self._sync_external_emergency_state()

        if self._stop_requested or self._emergency_stop_requested:
            return True

        if self.stop_callback is None:
            return False

        return bool(self.stop_callback())

    def _sync_external_emergency_state(self) -> None:
        """Sincroniza el estado de emergencia desde controller o checker externo."""
        if self.emergency_stop_controller.is_triggered:
            self._handle_emergency_stop({"source": "controller"})

        if self.emergency_stop_checker is not None and self.emergency_stop_checker():
            self._handle_emergency_stop({"source": "checker"})

    def _handle_emergency_stop(self, data: dict[str, Any] | None = None) -> None:
        """Marca y registra una parada de emergencia una sola vez."""
        self._emergency_stop_requested = True
        self._stop_requested = True

        if self._emergency_event_logged:
            return

        self._emergency_event_logged = True
        self._emit(
            "emergency_stop_triggered",
            "Parada de emergencia solicitada",
            data or {"source": "unknown"},
        )

    def _stop_if_requested(
        self,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> bool:
        """Registra la detención una sola vez cuando se alcanza un punto seguro."""
        if not self._should_stop():
            return False

        self._stop_requested = True
        if not self._stop_event_logged:
            self._stop_event_logged = True
            self._emit("stop_requested", message, data)

        return True

    def _finish_stopped(self) -> list[RunnerEvent]:
        """Registra el cierre seguro de una macro detenida y devuelve eventos."""
        self._emit(
            "macro_stopped",
            "Macro detenida de forma segura",
            {"emergency_stop": self._emergency_stop_requested},
        )
        return self.events

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
    """Valida y devuelve la variación aprobada para Fase 7."""
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


def _to_positive_float(value: object, field_name: str) -> float:
    """Convierte a float rechazando booleanos, textos inválidos y cero/negativos."""
    numeric_value = _to_non_negative_float(value, field_name)
    if numeric_value <= 0:
        raise ValueError(f"{field_name} debe ser mayor que cero")

    return numeric_value


__all__ = [
    "EXECUTION_MODE_REAL",
    "EXECUTION_MODE_TEST_LOG",
    "EXECUTION_MODE_TEST_KEYS",
    "EXECUTION_MODE_TEST_LOG_ONLY",
    "EXECUTION_MODE_TEST_KEYS_AND_LOG",
    "EXECUTION_MODE_LABELS",
    "VARIATION_SECONDS",
    "DEFAULT_STOP_CHECK_INTERVAL",
    "EmergencyStopController",
    "MacroRunner",
    "get_execution_mode_label",
    "get_randomized_delay",
    "create_runner_event",
]
