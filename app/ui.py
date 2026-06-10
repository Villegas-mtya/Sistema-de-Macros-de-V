"""Interfaz inicial funcional de Sistema de Macros de V.

Fase 8 integra de forma controlada tres piezas ya existentes del proyecto:

1. ``app.macro_storage`` para cargar una plantilla de macro en memoria.
2. ``app.preview`` para mostrar una previsualización segura antes de ejecutar.
3. ``app.macro_runner`` para ejecutar una simulación ``test_log`` sin pulsar teclas.

La interfaz no usa ``pynput.Controller``, no presiona teclas reales y bloquea de forma
explícita los modos ``real`` y ``test_keys``. El botón visual "Detener ahora" solo
solicita una parada segura al runner activo, sin depender de F9.
"""

from __future__ import annotations

import copy
import queue
import threading
from typing import Any
from tkinter import messagebox

import customtkinter as ctk

from app import APP_NAME
from app.app_paths import (
    get_config_dir,
    get_logs_dir,
    get_macros_dir,
    get_user_data_dir,
)
from app.macro_runner import MacroRunner, RunnerEvent
from app.macro_storage import get_default_macro_template
from app.preview import build_macro_preview, format_seconds

ALLOWED_UI_EXECUTION_MODE = "test_log"
BLOCKED_EXECUTION_MODES = {"real", "test_keys"}
LOG_POLL_INTERVAL_MS = 100


class MacroApp(ctk.CTk):
    """Ventana principal de Fase 8 con previsualización y runner test_log."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1180x760")
        self.minsize(1060, 680)

        self.current_macro: dict[str, Any] = self._create_test_log_template()
        self.current_runner: MacroRunner | None = None
        self.runner_thread: threading.Thread | None = None
        self.runner_events: queue.Queue[RunnerEvent] = queue.Queue()

        self.status_label: ctk.CTkLabel
        self.preview_textbox: ctk.CTkTextbox
        self.log_textbox: ctk.CTkTextbox
        self.run_button: ctk.CTkButton
        self.stop_button: ctk.CTkButton
        self.preview_button: ctk.CTkButton
        self.load_template_button: ctk.CTkButton

        self._build_layout()
        self._append_log_line("UI lista. Carga la plantilla, previsualiza o ejecuta una prueba solo log.")
        self._render_preview()
        self.after(LOG_POLL_INTERVAL_MS, self._poll_runner_events)

    def _create_test_log_template(self) -> dict[str, Any]:
        """Devuelve una plantilla segura para UI forzando ``execution_mode=test_log``."""
        macro_template = get_default_macro_template()
        macro_template["execution_mode"] = ALLOWED_UI_EXECUTION_MODE
        return macro_template

    def _build_layout(self) -> None:
        """Construye la pantalla principal con paneles simples y estado visible."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_content()

    def _build_header(self) -> None:
        """Crea encabezado y mensaje de seguridad de la fase actual."""
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text=APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w", padx=24, pady=(18, 4))

        subtitle = ctk.CTkLabel(
            header,
            text=(
                "Fase 8: previsualización y ejecución segura en modo prueba solo log. "
                "No se presionan teclas reales."
            ),
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 18))

    def _build_content(self) -> None:
        """Organiza controles, previsualización, rutas y log en dos columnas."""
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=24)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(1, weight=1)

        self._build_status_panel(content)
        self._build_action_panel(content)
        self._build_preview_panel(content)
        self._build_log_panel(content)

    def _build_status_panel(self, parent: ctk.CTkFrame) -> None:
        """Muestra estado claro y rutas seguras ya configuradas."""
        status_panel = ctk.CTkFrame(parent)
        status_panel.grid(row=0, column=0, sticky="ew", padx=(18, 9), pady=(18, 10))
        status_panel.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_panel,
            text="Estado: plantilla test_log cargada",
            fg_color=("#dbeafe", "#1e3a8a"),
            corner_radius=8,
            padx=14,
            pady=8,
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))

        paths_text = (
            f"Datos de usuario: {get_user_data_dir()}\n"
            f"Macros: {get_macros_dir()}\n"
            f"Logs: {get_logs_dir()}\n"
            f"Configuración: {get_config_dir()}"
        )
        paths_label = ctk.CTkLabel(status_panel, text=paths_text, justify="left", anchor="w")
        paths_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))

    def _build_action_panel(self, parent: ctk.CTkFrame) -> None:
        """Crea botones de plantilla, previsualización, ejecución y detención."""
        action_panel = ctk.CTkFrame(parent)
        action_panel.grid(row=1, column=0, sticky="nsew", padx=(18, 9), pady=(0, 18))
        action_panel.grid_columnconfigure(0, weight=1)

        section_title = ctk.CTkLabel(
            action_panel,
            text="Controles de Fase 8",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        section_title.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))

        self.load_template_button = ctk.CTkButton(
            action_panel,
            text="Cargar plantilla",
            command=self._load_template,
        )
        self.load_template_button.grid(row=1, column=0, sticky="ew", padx=14, pady=6)

        self.preview_button = ctk.CTkButton(
            action_panel,
            text="Previsualizar",
            command=self._render_preview,
        )
        self.preview_button.grid(row=2, column=0, sticky="ew", padx=14, pady=6)

        self.run_button = ctk.CTkButton(
            action_panel,
            text="Ejecutar prueba solo log",
            command=self._start_test_log_run,
        )
        self.run_button.grid(row=3, column=0, sticky="ew", padx=14, pady=6)

        self.stop_button = ctk.CTkButton(
            action_panel,
            text="Detener ahora",
            command=self._stop_runner,
            state="disabled",
            fg_color=("#dc2626", "#991b1b"),
            hover_color=("#b91c1c", "#7f1d1d"),
        )
        self.stop_button.grid(row=4, column=0, sticky="ew", padx=14, pady=6)

        safety_text = (
            "Seguridad activa:\n"
            "• La UI fuerza execution_mode = test_log.\n"
            "• Los modos real y test_keys se rechazan.\n"
            "• No hay pynput.Controller ni pulsación real de teclas.\n"
            "• Detener ahora llama a runner.stop()."
        )
        safety_label = ctk.CTkLabel(action_panel, text=safety_text, justify="left", anchor="nw")
        safety_label.grid(row=5, column=0, sticky="nsew", padx=14, pady=(14, 14))

    def _build_preview_panel(self, parent: ctk.CTkFrame) -> None:
        """Crea el panel de previsualización visible de la macro en memoria."""
        preview_panel = ctk.CTkFrame(parent)
        preview_panel.grid(row=0, column=1, sticky="nsew", padx=(9, 18), pady=(18, 10))
        preview_panel.grid_columnconfigure(0, weight=1)
        preview_panel.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            preview_panel,
            text="Previsualización de macro",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))

        self.preview_textbox = ctk.CTkTextbox(preview_panel, height=220, wrap="word")
        self.preview_textbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.preview_textbox.configure(state="disabled")

    def _build_log_panel(self, parent: ctk.CTkFrame) -> None:
        """Crea el log con scroll donde llegan eventos del runner."""
        log_panel = ctk.CTkFrame(parent)
        log_panel.grid(row=1, column=1, sticky="nsew", padx=(9, 18), pady=(0, 18))
        log_panel.grid_columnconfigure(0, weight=1)
        log_panel.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            log_panel,
            text="Log visible",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))

        self.log_textbox = ctk.CTkTextbox(log_panel, wrap="word")
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.log_textbox.configure(state="disabled")

    def _load_template(self) -> None:
        """Carga una plantilla limpia en memoria y actualiza la previsualización."""
        if self._is_runner_active():
            self._show_error("No se puede cargar otra plantilla mientras la prueba está activa.")
            return

        self.current_macro = self._create_test_log_template()
        self._set_status("Estado: plantilla test_log cargada")
        self._append_log_line("Plantilla cargada en memoria con execution_mode=test_log.")
        self._render_preview()

    def _render_preview(self) -> None:
        """Genera y muestra la previsualización usando ``build_macro_preview()``."""
        try:
            safe_macro = self._get_safe_test_log_macro()
            preview = build_macro_preview(safe_macro)
        except Exception as error:  # noqa: BLE001 - se muestra el error en UI.
            self._show_error(f"No se pudo previsualizar la macro: {error}")
            return

        preview_text = self._format_preview(preview)
        self._replace_textbox_content(self.preview_textbox, preview_text)
        self._set_status("Estado: previsualización generada")
        self._append_log_line("Previsualización generada correctamente.")

    def _get_safe_test_log_macro(self) -> dict[str, Any]:
        """Valida el modo de ejecución y devuelve una copia segura para Fase 8.

        La UI no permite ejecutar ni previsualizar modos peligrosos. Si una fase
        futura carga macros externas, este punto seguirá bloqueando ``real`` y
        ``test_keys`` antes de que lleguen al runner visual.
        """
        macro_copy = copy.deepcopy(self.current_macro)
        execution_mode = macro_copy.get("execution_mode")

        if execution_mode in BLOCKED_EXECUTION_MODES:
            raise ValueError(
                f"El modo {execution_mode!r} sigue bloqueado en Fase 8. "
                "Solo se permite 'test_log'."
            )

        if execution_mode != ALLOWED_UI_EXECUTION_MODE:
            macro_copy["execution_mode"] = ALLOWED_UI_EXECUTION_MODE

        return macro_copy

    def _format_preview(self, preview: dict[str, Any]) -> str:
        """Convierte el dict de previsualización en texto legible para pantalla."""
        duration = preview["duration_estimate"]
        if preview["infinite"]:
            duration_text = (
                "infinita; ciclo estimado "
                f"{self._format_duration_range(duration['per_cycle'])}"
            )
        else:
            duration_text = self._format_duration_range(duration["total"])

        action_lines = []
        for action in preview["actions"]:
            action_lines.append(
                f"  {action['index']}. Tecla {action['key_display_name']} "
                f"({action['key']}) — delay {action['delay_range_text']}"
            )

        actions_text = "\n".join(action_lines) if action_lines else "  Sin acciones configuradas."

        return (
            f"App: {preview['app']}\n"
            f"Versión: {preview['version']}\n"
            f"Número de acciones: {preview['actions_count']}\n"
            f"Repeticiones: {preview['repetitions']}\n"
            f"Infinita: {'sí' if preview['infinite'] else 'no'}\n"
            f"Modo de ejecución: {preview['execution_mode']}\n"
            f"Modo de selección de teclas: {preview['key_selection_mode']}\n"
            f"Duración estimada: {duration_text}\n\n"
            "Acciones:\n"
            f"{actions_text}"
        )

    def _format_duration_range(self, duration_range: dict[str, float] | None) -> str:
        """Formatea un rango de duración devuelto por ``app.preview``."""
        if duration_range is None:
            return "sin límite"

        return (
            f"mín {format_seconds(duration_range['min'])} / "
            f"prom {format_seconds(duration_range['avg'])} / "
            f"máx {format_seconds(duration_range['max'])}"
        )

    def _start_test_log_run(self) -> None:
        """Inicia MacroRunner en un hilo daemon para no congelar la UI."""
        if self._is_runner_active():
            self._show_error("Ya hay una prueba en ejecución.")
            return

        try:
            safe_macro = self._get_safe_test_log_macro()
            if safe_macro.get("execution_mode") != ALLOWED_UI_EXECUTION_MODE:
                raise ValueError("La Fase 8 solo permite execution_mode='test_log'.")
        except Exception as error:  # noqa: BLE001 - se informa al usuario.
            self._show_error(f"No se puede ejecutar la macro: {error}")
            return

        self.current_runner = MacroRunner(
            safe_macro,
            log_callback=self._enqueue_runner_event,
            enable_emergency_listener=False,
        )
        self.runner_thread = threading.Thread(
            target=self._run_macro_safely,
            daemon=True,
            name="MacroRunnerTestLogUI",
        )
        self.runner_thread.start()

        self._set_running_state(True)
        self._append_log_line("Prueba test_log iniciada en segundo plano.")

    def _run_macro_safely(self) -> None:
        """Ejecuta el runner y transforma errores en eventos visibles para la UI."""
        runner = self.current_runner
        if runner is None:
            self._enqueue_runner_event(
                {"type": "error", "message": "No hay runner activo", "data": {}}
            )
            return

        try:
            runner.run()
        except Exception as error:  # noqa: BLE001 - el error debe verse en el log.
            self._enqueue_runner_event(
                {
                    "type": "error",
                    "message": f"Error durante la prueba: {error}",
                    "data": {"error_type": type(error).__name__},
                }
            )
        finally:
            self._enqueue_runner_event(
                {"type": "ui_runner_thread_finished", "message": "Hilo de prueba finalizado", "data": {}}
            )

    def _stop_runner(self) -> None:
        """Solicita detención visual sin depender de F9."""
        if self.current_runner is None or not self._is_runner_active():
            self._append_log_line("No hay una prueba activa para detener.")
            self._set_running_state(False)
            return

        self.current_runner.stop()
        self._append_log_line("Detención solicitada desde el botón visual 'Detener ahora'.")
        self._set_status("Estado: detención solicitada")

    def _enqueue_runner_event(self, event: RunnerEvent) -> None:
        """Recibe eventos desde el hilo del runner sin tocar widgets directamente."""
        self.runner_events.put(event)

    def _poll_runner_events(self) -> None:
        """Procesa en el hilo de UI los eventos pendientes del runner."""
        runner_finished = False

        while True:
            try:
                event = self.runner_events.get_nowait()
            except queue.Empty:
                break

            if event["type"] == "ui_runner_thread_finished":
                runner_finished = True
            else:
                self._append_log_line(self._format_runner_event(event))

        if runner_finished:
            self._set_running_state(False)
            self._set_status("Estado: prueba finalizada")
            self.current_runner = None
            self.runner_thread = None

        self.after(LOG_POLL_INTERVAL_MS, self._poll_runner_events)

    def _format_runner_event(self, event: RunnerEvent) -> str:
        """Devuelve una línea de log clara para eventos de ``MacroRunner``."""
        event_type = event.get("type", "evento")
        message = event.get("message", "")
        data = event.get("data") or {}
        details = self._format_event_data(data)

        if details:
            return f"[{event_type}] {message} | {details}"

        return f"[{event_type}] {message}"

    def _format_event_data(self, data: dict[str, Any]) -> str:
        """Resume datos frecuentes del runner sin saturar el log visual."""
        visible_parts = []
        for key in (
            "repetition",
            "action_index",
            "key_display_name",
            "delay_seconds",
            "variation_mode",
            "emergency_stop",
            "source",
            "error_type",
        ):
            if key in data:
                visible_parts.append(f"{key}={data[key]}")

        return ", ".join(visible_parts)

    def _is_runner_active(self) -> bool:
        """Indica si el hilo del runner sigue vivo."""
        return self.runner_thread is not None and self.runner_thread.is_alive()

    def _set_running_state(self, is_running: bool) -> None:
        """Habilita/deshabilita botones según haya una prueba activa."""
        run_state = "disabled" if is_running else "normal"
        stop_state = "normal" if is_running else "disabled"

        self.run_button.configure(state=run_state)
        self.preview_button.configure(state=run_state)
        self.load_template_button.configure(state=run_state)
        self.stop_button.configure(state=stop_state)

        if is_running:
            self._set_status("Estado: prueba test_log en ejecución")

    def _set_status(self, text: str) -> None:
        """Actualiza el badge de estado principal."""
        self.status_label.configure(text=text)

    def _replace_textbox_content(self, textbox: ctk.CTkTextbox, text: str) -> None:
        """Reemplaza contenido de un textbox de solo lectura de forma segura."""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")

    def _append_log_line(self, text: str) -> None:
        """Agrega una línea al log visible y mantiene el scroll al final."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{text}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def _show_error(self, message: str) -> None:
        """Muestra errores por messagebox y también en el log para trazabilidad."""
        self._append_log_line(f"ERROR: {message}")
        messagebox.showerror(APP_NAME, message)


def run_app() -> None:
    """Configura CustomTkinter y abre la ventana principal."""
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MacroApp()
    app.mainloop()
