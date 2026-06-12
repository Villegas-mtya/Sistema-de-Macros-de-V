"""Interfaz principal de Sistema de Macros de V.

Fase 11 refina el constructor seguro de Fase 10.
La pantalla permite crear y editar acciones de teclado, reordenarlas,
guardar/cargar macros JSON, importar/exportar archivos, previsualizar los datos
actuales y ejecutar en ``test_log`` o en modo ``real`` controlado. La UI exige
selección explícita y confirmación visual antes de presionar teclas reales.
"""

from __future__ import annotations

import copy
import json
import queue
import threading
from pathlib import Path
from typing import Any
from tkinter import BooleanVar, IntVar, StringVar, filedialog, messagebox

import customtkinter as ctk

from app import APP_NAME
from app.app_paths import (
    get_config_dir,
    get_logs_dir,
    get_macros_dir,
    get_user_data_dir,
)
from app.key_mapper import (
    get_key_display_name,
    get_simple_key_options,
    normalize_key,
    validate_key,
)
from app.macro_runner import (
    EXECUTION_MODE_REAL,
    EXECUTION_MODE_TEST_LOG,
    EXECUTION_MODE_TEST_KEYS,
    MacroRunner,
    RunnerEvent,
)
from app.macro_storage import (
    delete_macro,
    export_macro,
    get_default_macro_template,
    import_macro,
    list_saved_macros,
    load_macro,
    save_macro,
)
from app.preview import build_macro_preview, format_seconds
from app.validators import validate_macro_data

DEFAULT_UI_EXECUTION_MODE = EXECUTION_MODE_TEST_LOG
ALLOWED_UI_EXECUTION_MODES = {EXECUTION_MODE_TEST_LOG, EXECUTION_MODE_REAL}
BLOCKED_EXECUTION_MODES = {EXECUTION_MODE_TEST_KEYS}
EXECUTION_MODE_VALUES_BY_LABEL = {
    "Prueba solo log / test_log": EXECUTION_MODE_TEST_LOG,
    "Ejecución real / real": EXECUTION_MODE_REAL,
}
EXECUTION_MODE_LABELS_BY_VALUE = {
    value: label for label, value in EXECUTION_MODE_VALUES_BY_LABEL.items()
}
EXECUTION_MODE_LABELS = list(EXECUTION_MODE_VALUES_BY_LABEL)
LOG_POLL_INTERVAL_MS = 100

VARIATION_LABELS_BY_VALUE = {
    "fixed": "Sin variación",
    "light": "Ligera",
    "medium": "Media",
    "high": "Alta",
}
VARIATION_VALUES_BY_LABEL = {label: value for value, label in VARIATION_LABELS_BY_VALUE.items()}
VARIATION_LABELS = list(VARIATION_VALUES_BY_LABEL)
KEY_SELECTION_MODES = ("simple", "advanced")


class MacroApp(ctk.CTk):
    """Ventana principal con edición visual y ejecución controlada de Fase 22."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1280x820")
        self.minsize(1160, 720)

        self.current_macro: dict[str, Any] = self._create_test_log_template()
        self.actions: list[dict[str, Any]] = copy.deepcopy(self.current_macro["actions"])
        self.current_runner: MacroRunner | None = None
        self.runner_thread: threading.Thread | None = None
        self.runner_events: queue.Queue[RunnerEvent] = queue.Queue()

        self.simple_key_options = get_simple_key_options()

        self.execution_mode_var = StringVar(value=EXECUTION_MODE_LABELS_BY_VALUE[DEFAULT_UI_EXECUTION_MODE])
        self.execution_mode_var.trace_add("write", self._on_execution_mode_changed)
        self.key_selection_mode_var = StringVar(value=self.current_macro["key_selection_mode"])
        self.simple_key_var = StringVar(value=self.simple_key_options[0])
        self.advanced_key_var = StringVar(value="enter")
        self.action_delay_var = StringVar(value="1.0")
        self.action_variation_var = StringVar(value=VARIATION_LABELS_BY_VALUE["fixed"])
        self.initial_delay_var = StringVar(value=str(float(self.current_macro["initial_delay"])))
        self.repetitions_var = StringVar(value=str(int(self.current_macro["repetitions"])))
        self.infinite_var = BooleanVar(value=bool(self.current_macro["infinite"]))
        self.cooldown_base_var = StringVar(value=str(float(self.current_macro["cooldown_base"])))
        self.cooldown_variation_var = StringVar(
            value=VARIATION_LABELS_BY_VALUE[self.current_macro["cooldown_variation"]]
        )
        self.selected_action_index_var = IntVar(value=0)
        self.is_loading_action_selection = False
        self.selected_action_index_var.trace_add("write", self._on_action_selection_changed)
        self.macro_name_var = StringVar(value="macro_prueba")
        self.saved_macro_var = StringVar(value="Sin macros guardadas")
        self.saved_macros: list[dict[str, str]] = []

        self.status_label: ctk.CTkLabel
        self.preview_textbox: ctk.CTkTextbox
        self.log_textbox: ctk.CTkTextbox
        self.run_button: ctk.CTkButton
        self.stop_button: ctk.CTkButton
        self.preview_button: ctk.CTkButton
        self.load_template_button: ctk.CTkButton
        self.add_action_button: ctk.CTkButton
        self.update_action_button: ctk.CTkButton
        self.clear_selection_button: ctk.CTkButton
        self.move_action_up_button: ctk.CTkButton
        self.move_action_down_button: ctk.CTkButton
        self.duplicate_action_button: ctk.CTkButton
        self.delete_action_button: ctk.CTkButton
        self.clear_actions_button: ctk.CTkButton
        self.save_macro_button: ctk.CTkButton
        self.refresh_macros_button: ctk.CTkButton
        self.load_macro_button: ctk.CTkButton
        self.delete_macro_button: ctk.CTkButton
        self.import_json_button: ctk.CTkButton
        self.export_json_button: ctk.CTkButton
        self.saved_macros_menu: ctk.CTkOptionMenu
        self.execution_mode_menu: ctk.CTkOptionMenu
        self.simple_key_menu: ctk.CTkOptionMenu
        self.advanced_key_entry: ctk.CTkEntry
        self.actions_list_frame: ctk.CTkScrollableFrame
        self.action_count_label: ctk.CTkLabel

        self._build_layout()
        self._sync_key_input_state()
        self._render_actions_list()
        self._refresh_saved_macros(log_result=False)
        self._append_log_line(
            "UI lista. El modo por defecto es test_log; cambia a real solo si quieres presionar teclas reales."
        )
        self._render_preview()
        self.after(LOG_POLL_INTERVAL_MS, self._poll_runner_events)

    def _create_test_log_template(self) -> dict[str, Any]:
        """Devuelve una plantilla segura para UI forzando ``execution_mode=test_log``."""
        macro_template = get_default_macro_template()
        macro_template["execution_mode"] = DEFAULT_UI_EXECUTION_MODE
        macro_template["key_selection_mode"] = "simple"
        return macro_template

    def _build_layout(self) -> None:
        """Construye la pantalla principal con paneles claros y redimensionables."""
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
                "Fase 22: test_log por defecto y ejecución real de teclado solo con "
                "selección explícita y confirmación manual."
            ),
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 18))

    def _build_content(self) -> None:
        """Organiza constructor, configuración, previsualización y log."""
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=24)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(1, weight=1)

        self._build_status_panel(content)
        self._build_builder_panel(content)
        self._build_preview_panel(content)
        self._build_log_panel(content)

    def _build_status_panel(self, parent: ctk.CTkFrame) -> None:
        """Muestra estado claro y rutas seguras ya configuradas."""
        status_panel = ctk.CTkFrame(parent)
        status_panel.grid(row=0, column=0, sticky="ew", padx=(18, 9), pady=(18, 10))
        status_panel.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_panel,
            text="Estado: constructor listo; modo por defecto test_log",
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

    def _build_builder_panel(self, parent: ctk.CTkFrame) -> None:
        """Crea el constructor manual y los controles de ejecución segura."""
        builder_panel = ctk.CTkScrollableFrame(parent)
        builder_panel.grid(row=1, column=0, sticky="nsew", padx=(18, 9), pady=(0, 18))
        builder_panel.grid_columnconfigure(0, weight=1)

        section_title = ctk.CTkLabel(
            builder_panel,
            text="Constructor de macro",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        section_title.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))

        self._build_action_editor(builder_panel, row=1)
        self._build_actions_list(builder_panel, row=2)
        self._build_macro_config(builder_panel, row=3)
        self._build_saved_macros_panel(builder_panel, row=4)
        self._build_execution_controls(builder_panel, row=5)

    def _build_action_editor(self, parent: ctk.CTkFrame, row: int) -> None:
        """Crea controles para agregar una acción manualmente."""
        editor = ctk.CTkFrame(parent)
        editor.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        editor.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(editor, text="Editor de acción", font=ctk.CTkFont(weight="bold"), anchor="w")
        title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))

        ctk.CTkLabel(editor, text="Modo de tecla", anchor="w").grid(
            row=1, column=0, sticky="w", padx=12, pady=4
        )
        mode_frame = ctk.CTkFrame(editor, fg_color="transparent")
        mode_frame.grid(row=1, column=1, sticky="ew", padx=12, pady=4)
        ctk.CTkRadioButton(
            mode_frame,
            text="Simple",
            value="simple",
            variable=self.key_selection_mode_var,
            command=self._sync_key_input_state,
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))
        ctk.CTkRadioButton(
            mode_frame,
            text="Avanzado",
            value="advanced",
            variable=self.key_selection_mode_var,
            command=self._sync_key_input_state,
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(editor, text="Tecla simple", anchor="w").grid(
            row=2, column=0, sticky="w", padx=12, pady=4
        )
        self.simple_key_menu = ctk.CTkOptionMenu(
            editor,
            values=self.simple_key_options,
            variable=self.simple_key_var,
        )
        self.simple_key_menu.grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        ctk.CTkLabel(editor, text="Tecla avanzada", anchor="w").grid(
            row=3, column=0, sticky="w", padx=12, pady=4
        )
        self.advanced_key_entry = ctk.CTkEntry(
            editor,
            textvariable=self.advanced_key_var,
            placeholder_text="Ej.: enter, F12, Flecha arriba, a, 5",
        )
        self.advanced_key_entry.grid(row=3, column=1, sticky="ew", padx=12, pady=4)

        ctk.CTkLabel(editor, text="Espera base", anchor="w").grid(
            row=4, column=0, sticky="w", padx=12, pady=4
        )
        ctk.CTkEntry(editor, textvariable=self.action_delay_var, placeholder_text="Segundos, ej. 1.0").grid(
            row=4, column=1, sticky="ew", padx=12, pady=4
        )

        ctk.CTkLabel(editor, text="Variación", anchor="w").grid(
            row=5, column=0, sticky="w", padx=12, pady=4
        )
        ctk.CTkOptionMenu(
            editor,
            values=VARIATION_LABELS,
            variable=self.action_variation_var,
        ).grid(row=5, column=1, sticky="ew", padx=12, pady=4)

        action_buttons = ctk.CTkFrame(editor, fg_color="transparent")
        action_buttons.grid(row=6, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 12))
        for column in range(3):
            action_buttons.grid_columnconfigure(column, weight=1)

        self.add_action_button = ctk.CTkButton(
            action_buttons,
            text="Agregar acción",
            command=self._add_action,
        )
        self.add_action_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.update_action_button = ctk.CTkButton(
            action_buttons,
            text="Actualizar acción",
            command=self._update_selected_action,
        )
        self.update_action_button.grid(row=0, column=1, sticky="ew", padx=6)

        self.clear_selection_button = ctk.CTkButton(
            action_buttons,
            text="Limpiar selección",
            command=self._clear_action_selection,
        )
        self.clear_selection_button.grid(row=0, column=2, sticky="ew", padx=(6, 0))

    def _build_actions_list(self, parent: ctk.CTkFrame, row: int) -> None:
        """Crea una lista visual seleccionable de acciones configuradas."""
        list_panel = ctk.CTkFrame(parent)
        list_panel.grid(row=row, column=0, sticky="nsew", padx=14, pady=(0, 10))
        list_panel.grid_columnconfigure(0, weight=1)
        list_panel.grid_rowconfigure(2, weight=1)

        self.action_count_label = ctk.CTkLabel(
            list_panel,
            text="Acciones configuradas: 0",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        )
        self.action_count_label.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        header = ctk.CTkLabel(
            list_panel,
            text="# | Tecla | Espera base | Variación",
            anchor="w",
            fg_color=("#e5e7eb", "#374151"),
            corner_radius=6,
            padx=8,
            pady=4,
        )
        header.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))

        self.actions_list_frame = ctk.CTkScrollableFrame(list_panel, height=150)
        self.actions_list_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))
        self.actions_list_frame.grid_columnconfigure(0, weight=1)

        buttons = ctk.CTkFrame(list_panel, fg_color="transparent")
        buttons.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 12))
        for column in range(5):
            buttons.grid_columnconfigure(column, weight=1)

        self.move_action_up_button = ctk.CTkButton(
            buttons,
            text="Subir acción",
            command=self._move_selected_action_up,
        )
        self.move_action_up_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.move_action_down_button = ctk.CTkButton(
            buttons,
            text="Bajar acción",
            command=self._move_selected_action_down,
        )
        self.move_action_down_button.grid(row=0, column=1, sticky="ew", padx=4)

        self.duplicate_action_button = ctk.CTkButton(
            buttons,
            text="Duplicar acción",
            command=self._duplicate_selected_action,
        )
        self.duplicate_action_button.grid(row=0, column=2, sticky="ew", padx=4)

        self.delete_action_button = ctk.CTkButton(
            buttons,
            text="Eliminar acción",
            command=self._delete_selected_or_last_action,
        )
        self.delete_action_button.grid(row=0, column=3, sticky="ew", padx=4)

        self.clear_actions_button = ctk.CTkButton(
            buttons,
            text="Limpiar acciones",
            command=self._clear_actions,
            fg_color=("#92400e", "#78350f"),
            hover_color=("#78350f", "#451a03"),
        )
        self.clear_actions_button.grid(row=0, column=4, sticky="ew", padx=(4, 0))

    def _build_macro_config(self, parent: ctk.CTkFrame, row: int) -> None:
        """Crea controles de delays, repeticiones y cooldown de la macro."""
        config = ctk.CTkFrame(parent)
        config.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        config.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(config, text="Configuración de macro", font=ctk.CTkFont(weight="bold"), anchor="w")
        title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))

        self._add_labeled_entry(config, "Delay inicial", self.initial_delay_var, 1)
        self._add_labeled_entry(config, "Repeticiones", self.repetitions_var, 2)

        ctk.CTkLabel(config, text="Infinita", anchor="w").grid(
            row=3, column=0, sticky="w", padx=12, pady=4
        )
        ctk.CTkCheckBox(
            config,
            text="Ignorar repeticiones y repetir hasta detener",
            variable=self.infinite_var,
        ).grid(row=3, column=1, sticky="w", padx=12, pady=4)

        self._add_labeled_entry(config, "Cooldown base", self.cooldown_base_var, 4)

        ctk.CTkLabel(config, text="Variación cooldown", anchor="w").grid(
            row=5, column=0, sticky="w", padx=12, pady=(4, 12)
        )
        ctk.CTkOptionMenu(
            config,
            values=VARIATION_LABELS,
            variable=self.cooldown_variation_var,
        ).grid(row=5, column=1, sticky="ew", padx=12, pady=(4, 12))

    def _build_saved_macros_panel(self, parent: ctk.CTkFrame, row: int) -> None:
        """Crea la sección visual de Fase 10 para guardar, cargar e intercambiar JSON."""
        storage = ctk.CTkFrame(parent)
        storage.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        storage.grid_columnconfigure(0, weight=1)
        storage.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(storage, text="Macros guardadas", font=ctk.CTkFont(weight="bold"), anchor="w")
        title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))

        ctk.CTkLabel(storage, text="Nombre de macro", anchor="w").grid(
            row=1, column=0, sticky="w", padx=12, pady=4
        )
        ctk.CTkEntry(
            storage,
            textvariable=self.macro_name_var,
            placeholder_text="Ej.: macro_prueba",
        ).grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        self.save_macro_button = ctk.CTkButton(
            storage,
            text="Guardar macro",
            command=self._save_current_macro,
        )
        self.save_macro_button.grid(row=2, column=0, sticky="ew", padx=12, pady=4)

        self.refresh_macros_button = ctk.CTkButton(
            storage,
            text="Actualizar lista",
            command=self._refresh_saved_macros,
        )
        self.refresh_macros_button.grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        ctk.CTkLabel(storage, text="Macro guardada", anchor="w").grid(
            row=3, column=0, sticky="w", padx=12, pady=4
        )
        self.saved_macros_menu = ctk.CTkOptionMenu(
            storage,
            values=[self.saved_macro_var.get()],
            variable=self.saved_macro_var,
        )
        self.saved_macros_menu.grid(row=3, column=1, sticky="ew", padx=12, pady=4)

        self.load_macro_button = ctk.CTkButton(
            storage,
            text="Cargar macro",
            command=self._load_selected_saved_macro,
        )
        self.load_macro_button.grid(row=4, column=0, sticky="ew", padx=12, pady=4)

        self.delete_macro_button = ctk.CTkButton(
            storage,
            text="Eliminar macro",
            command=self._delete_selected_saved_macro,
            fg_color=("#92400e", "#78350f"),
            hover_color=("#78350f", "#451a03"),
        )
        self.delete_macro_button.grid(row=4, column=1, sticky="ew", padx=12, pady=4)

        self.import_json_button = ctk.CTkButton(
            storage,
            text="Importar JSON",
            command=self._import_json_macro,
        )
        self.import_json_button.grid(row=5, column=0, sticky="ew", padx=12, pady=(4, 12))

        self.export_json_button = ctk.CTkButton(
            storage,
            text="Exportar JSON",
            command=self._export_json_macro,
        )
        self.export_json_button.grid(row=5, column=1, sticky="ew", padx=12, pady=(4, 12))

    def _build_execution_controls(self, parent: ctk.CTkFrame, row: int) -> None:
        """Crea botones de plantilla, previsualización, ejecución y detención."""
        controls = ctk.CTkFrame(parent)
        controls.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 14))
        controls.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(controls, text="Controles seguros", font=ctk.CTkFont(weight="bold"), anchor="w")
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        self.load_template_button = ctk.CTkButton(
            controls,
            text="Cargar plantilla",
            command=self._load_template,
        )
        self.load_template_button.grid(row=1, column=0, sticky="ew", padx=12, pady=4)

        self.preview_button = ctk.CTkButton(
            controls,
            text="Previsualizar",
            command=self._render_preview,
        )
        self.preview_button.grid(row=2, column=0, sticky="ew", padx=12, pady=4)

        ctk.CTkLabel(controls, text="Modo de ejecución", anchor="w").grid(
            row=3, column=0, sticky="w", padx=12, pady=(8, 2)
        )
        self.execution_mode_menu = ctk.CTkOptionMenu(
            controls,
            values=EXECUTION_MODE_LABELS,
            variable=self.execution_mode_var,
            command=lambda _value: self._on_execution_mode_changed(),
        )
        self.execution_mode_menu.grid(row=4, column=0, sticky="ew", padx=12, pady=4)

        self.run_button = ctk.CTkButton(
            controls,
            text="Ejecutar prueba solo log",
            command=self._start_macro_run,
        )
        self.run_button.grid(row=5, column=0, sticky="ew", padx=12, pady=4)

        self.stop_button = ctk.CTkButton(
            controls,
            text="Detener ahora",
            command=self._stop_runner,
            state="disabled",
            fg_color=("#dc2626", "#991b1b"),
            hover_color=("#b91c1c", "#7f1d1d"),
        )
        self.stop_button.grid(row=6, column=0, sticky="ew", padx=12, pady=4)

        safety_text = (
            "Seguridad activa:\n"
            "• test_log es el modo por defecto para probar sin presionar teclas.\n"
            "• real presiona teclas solo tras confirmación visual.\n"
            "• test_keys sigue bloqueado. No hay grabación, mouse, clicks ni movimientos.\n"
            "• Detener ahora llama a runner.stop(); F9 queda limitado a parada de emergencia."
        )
        ctk.CTkLabel(controls, text=safety_text, justify="left", anchor="nw").grid(
            row=7, column=0, sticky="ew", padx=12, pady=(10, 12)
        )

    def _build_preview_panel(self, parent: ctk.CTkFrame) -> None:
        """Crea el panel de previsualización visible de la macro editada."""
        preview_panel = ctk.CTkFrame(parent)
        preview_panel.grid(row=0, column=1, sticky="nsew", padx=(9, 18), pady=(18, 10))
        preview_panel.grid_columnconfigure(0, weight=1)
        preview_panel.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            preview_panel,
            text="Previsualización de macro editada",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))

        self.preview_textbox = ctk.CTkTextbox(preview_panel, height=260, wrap="word")
        self.preview_textbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.preview_textbox.configure(state="disabled")

    def _build_log_panel(self, parent: ctk.CTkFrame) -> None:
        """Crea el log con scroll donde llegan eventos del runner y de validación."""
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

    def _add_labeled_entry(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: StringVar,
        row: int,
    ) -> None:
        """Agrega una entrada de texto con etiqueta para campos numéricos."""
        ctk.CTkLabel(parent, text=label, anchor="w").grid(row=row, column=0, sticky="w", padx=12, pady=4)
        ctk.CTkEntry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=12, pady=4)

    def _sync_key_input_state(self) -> None:
        """Activa el control de tecla correspondiente al modo simple o avanzado."""
        mode = self.key_selection_mode_var.get()
        simple_state = "normal" if mode == "simple" else "disabled"
        advanced_state = "normal" if mode == "advanced" else "disabled"
        if hasattr(self, "simple_key_menu"):
            self.simple_key_menu.configure(state=simple_state)
        if hasattr(self, "advanced_key_entry"):
            self.advanced_key_entry.configure(state=advanced_state)

    def _save_current_macro(self) -> None:
        """Guarda la macro editada en la carpeta segura de macros de usuario."""
        if self._is_runner_active():
            self._show_error("No se puede guardar mientras la prueba está activa.")
            return

        macro_name = self._get_macro_name_from_entry()
        if macro_name is None:
            self._show_error("El nombre de macro no puede estar vacío.")
            return

        try:
            safe_macro = self._build_validated_macro_from_controls()
            saved_path = save_macro(safe_macro, macro_name)
        except (OSError, ValueError) as error:
            self._show_error(f"No se pudo guardar la macro: {error}")
            return

        self.current_macro = safe_macro
        self._refresh_saved_macros(selected_name=saved_path.stem, log_result=False)
        self._append_log_line(f"Macro guardada correctamente: {saved_path.name}.")
        self._set_status(f"Estado: macro guardada en modo {safe_macro['execution_mode']}")

    def _refresh_saved_macros(
        self,
        selected_name: str | None = None,
        log_result: bool = True,
    ) -> None:
        """Actualiza el selector visual usando ``list_saved_macros()``."""
        try:
            self.saved_macros = self._get_saved_macro_infos()
        except OSError as error:
            self._show_error(f"No se pudo actualizar la lista de macros: {error}")
            return

        option_names = [macro_info["name"] for macro_info in self.saved_macros]
        if not option_names:
            option_names = ["Sin macros guardadas"]
            self.saved_macro_var.set(option_names[0])
        elif selected_name in option_names:
            self.saved_macro_var.set(str(selected_name))
        elif self.saved_macro_var.get() not in option_names:
            self.saved_macro_var.set(option_names[0])

        if hasattr(self, "saved_macros_menu"):
            self.saved_macros_menu.configure(values=option_names)

        self._sync_saved_macro_buttons_state()
        if log_result:
            self._append_log_line(f"Lista de macros actualizada: {len(self.saved_macros)} archivo(s).")

    def _load_selected_saved_macro(self) -> None:
        """Carga una macro guardada al constructor visual y fuerza modo seguro."""
        if self._is_runner_active():
            self._show_error("No se puede cargar una macro mientras la prueba está activa.")
            return

        macro_info = self._get_selected_saved_macro_info()
        if macro_info is None:
            self._show_error("Selecciona una macro guardada para cargar.")
            return

        try:
            loaded_macro = load_macro(macro_info["file_name"])
            safe_macro = self._force_loaded_macro_to_test_log(loaded_macro, source_label=macro_info["file_name"])
        except (OSError, ValueError) as error:
            self._show_error(f"No se pudo cargar la macro: {error}")
            return

        self.current_macro = safe_macro
        self.macro_name_var.set(macro_info["name"])
        self._load_macro_into_controls(safe_macro)
        self._render_actions_list()
        self._render_preview()
        self._append_log_line(f"Macro cargada en el constructor: {macro_info['file_name']}.")
        self._set_status("Estado: macro cargada en modo test_log")

    def _delete_selected_saved_macro(self) -> None:
        """Elimina la macro seleccionada tras confirmación explícita."""
        if self._is_runner_active():
            self._show_error("No se puede eliminar una macro mientras la prueba está activa.")
            return

        macro_info = self._get_selected_saved_macro_info()
        if macro_info is None:
            self._show_error("Selecciona una macro guardada para eliminar.")
            return

        confirmed = messagebox.askyesno(
            "Eliminar macro",
            f"¿Quieres eliminar la macro guardada '{macro_info['file_name']}'?",
        )
        if not confirmed:
            self._append_log_line("Eliminación de macro cancelada por el usuario.")
            return

        try:
            delete_macro(macro_info["file_name"])
        except (OSError, ValueError) as error:
            self._show_error(f"No se pudo eliminar la macro: {error}")
            return

        self._refresh_saved_macros(log_result=False)
        self._append_log_line(f"Macro eliminada: {macro_info['file_name']}.")
        self._set_status("Estado: macro eliminada")

    def _import_json_macro(self) -> None:
        """Importa un JSON externo, actualiza la lista y carga la macro de forma segura."""
        if self._is_runner_active():
            self._show_error("No se puede importar una macro mientras la prueba está activa.")
            return

        source_path = filedialog.askopenfilename(
            title="Importar macro JSON",
            filetypes=(("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")),
        )
        if not source_path:
            self._append_log_line("Importación JSON cancelada por el usuario.")
            return

        try:
            imported_path = import_macro(source_path)
        except (OSError, ValueError) as error:
            self._show_error(f"No se pudo importar el JSON: {error}")
            return

        self._refresh_saved_macros(selected_name=imported_path.stem, log_result=False)
        self._append_log_line(f"Macro importada: {imported_path.name}.")
        self._load_imported_macro_into_constructor(imported_path)

    def _export_json_macro(self) -> None:
        """Exporta la macro seleccionada o, si no hay selección, la macro actual validada."""
        if self._is_runner_active():
            self._show_error("No se puede exportar una macro mientras la prueba está activa.")
            return

        macro_info = self._get_selected_saved_macro_info()
        default_name = macro_info["file_name"] if macro_info else f"{self._get_default_export_name()}.json"
        destination_path = filedialog.asksaveasfilename(
            title="Exportar macro JSON",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=(("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")),
        )
        if not destination_path:
            self._append_log_line("Exportación JSON cancelada por el usuario.")
            return

        try:
            if macro_info is not None:
                exported_path = export_macro(macro_info["file_name"], destination_path)
                self._append_log_line(
                    f"Macro guardada exportada: {macro_info['file_name']} -> {exported_path}."
                )
            else:
                exported_path = self._export_current_macro_to_json(destination_path)
                self._append_log_line(f"Macro actual exportada en modo {self.current_macro.get('execution_mode', DEFAULT_UI_EXECUTION_MODE)}: {exported_path}.")
        except (OSError, ValueError) as error:
            self._show_error(f"No se pudo exportar el JSON: {error}")
            return

        self._set_status("Estado: macro exportada a JSON")

    def _load_imported_macro_into_constructor(self, imported_path: Path) -> None:
        """Carga en pantalla el JSON recién importado, siempre forzando ``test_log``."""
        try:
            loaded_macro = load_macro(imported_path.name)
            safe_macro = self._force_loaded_macro_to_test_log(loaded_macro, source_label=imported_path.name)
        except (OSError, ValueError) as error:
            self._show_error(f"La macro se importó, pero no se pudo cargar en la UI: {error}")
            return

        self.current_macro = safe_macro
        self.macro_name_var.set(imported_path.stem)
        self._load_macro_into_controls(safe_macro)
        self._render_actions_list()
        self._render_preview()
        self._append_log_line(f"Macro importada cargada en el constructor: {imported_path.name}.")
        self._set_status("Estado: macro importada en modo test_log")

    def _export_current_macro_to_json(self, destination_path: str) -> Path:
        """Escribe la macro actual validada en un JSON externo sin crear una macro interna."""
        safe_macro = self._build_validated_macro_from_controls()
        destination = Path(destination_path).expanduser()
        if destination.suffix.lower() != ".json":
            destination = destination.with_suffix(".json")

        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as macro_file:
            json.dump(safe_macro, macro_file, ensure_ascii=False, indent=2)
            macro_file.write("\n")

        self.current_macro = safe_macro
        return destination.resolve()

    def _force_loaded_macro_to_test_log(self, macro_data: dict[str, Any], source_label: str) -> dict[str, Any]:
        """Convierte macros cargadas/importadas a ``test_log`` antes de usarlas en UI."""
        macro_copy = copy.deepcopy(macro_data)
        original_mode = macro_copy.get("execution_mode")
        if original_mode != DEFAULT_UI_EXECUTION_MODE:
            self._append_log_line(
                f"Modo seguro aplicado a {source_label}: execution_mode {original_mode!r} -> 'test_log'."
            )

        macro_copy["execution_mode"] = DEFAULT_UI_EXECUTION_MODE
        key_selection_mode = macro_copy.get("key_selection_mode")
        if key_selection_mode not in KEY_SELECTION_MODES:
            macro_copy["key_selection_mode"] = "simple"
            self._append_log_line(
                f"Modo de selección inválido en {source_label}; se usó 'simple'."
            )

        if not validate_macro_data(macro_copy):
            raise ValueError("La macro cargada no cumple la estructura válida para Fase 22")

        return macro_copy

    def _get_macro_name_from_entry(self) -> str | None:
        """Lee el nombre escrito por el usuario y rechaza valores vacíos."""
        macro_name = self.macro_name_var.get().strip()
        if not macro_name:
            return None
        return macro_name

    def _get_saved_macro_infos(self) -> list[dict[str, str]]:
        """Normaliza la salida de ``list_saved_macros()`` para el selector visual."""
        macro_infos: list[dict[str, str]] = []
        for item in list_saved_macros():
            if isinstance(item, dict):
                name = str(item["name"])
                file_name = str(item.get("file_name", f"{name}.json"))
                item_path = str(item.get("path", get_macros_dir() / file_name))
            else:
                item_path_object = Path(item)
                name = item_path_object.stem
                file_name = item_path_object.name
                item_path = str(item_path_object)

            macro_infos.append({"name": name, "file_name": file_name, "path": item_path})

        return macro_infos

    def _get_selected_saved_macro_info(self) -> dict[str, str] | None:
        """Devuelve la macro seleccionada o ``None`` si la lista está vacía."""
        selected_name = self.saved_macro_var.get()
        for macro_info in self.saved_macros:
            if macro_info["name"] == selected_name:
                return macro_info
        return None

    def _sync_saved_macro_buttons_state(self) -> None:
        """Habilita carga/borrado solo cuando existe una macro seleccionable."""
        has_saved_macros = bool(self.saved_macros)
        load_delete_state = "normal" if has_saved_macros and not self._is_runner_active() else "disabled"
        if hasattr(self, "load_macro_button"):
            self.load_macro_button.configure(state=load_delete_state)
        if hasattr(self, "delete_macro_button"):
            self.delete_macro_button.configure(state=load_delete_state)

    def _get_default_export_name(self) -> str:
        """Propone un nombre estable para exportar la macro actual."""
        macro_name = self._get_macro_name_from_entry()
        return macro_name or "macro_actual_test_log"

    def _load_template(self) -> None:
        """Carga una plantilla limpia en controles editables y actualiza la vista."""
        if self._is_runner_active():
            self._show_error("No se puede cargar otra plantilla mientras la prueba está activa.")
            return

        self.current_macro = self._create_test_log_template()
        self._load_macro_into_controls(self.current_macro)
        self._set_status("Estado: plantilla test_log cargada en el constructor")
        self._append_log_line("Plantilla cargada en controles con execution_mode=test_log.")
        self._render_actions_list()
        self._render_preview()

    def _load_macro_into_controls(self, macro_data: dict[str, Any]) -> None:
        """Copia una macro validada o plantilla hacia los controles de Fase 11."""
        self.actions = copy.deepcopy(macro_data.get("actions", []))
        execution_mode = macro_data.get("execution_mode", DEFAULT_UI_EXECUTION_MODE)
        if execution_mode not in ALLOWED_UI_EXECUTION_MODES:
            execution_mode = DEFAULT_UI_EXECUTION_MODE
        self.execution_mode_var.set(EXECUTION_MODE_LABELS_BY_VALUE[execution_mode])
        self.key_selection_mode_var.set(macro_data.get("key_selection_mode", "simple"))
        self.initial_delay_var.set(str(float(macro_data.get("initial_delay", 0.0))))
        self.repetitions_var.set(str(int(macro_data.get("repetitions", 1))))
        self.infinite_var.set(bool(macro_data.get("infinite", False)))
        self.cooldown_base_var.set(str(float(macro_data.get("cooldown_base", 0.0))))
        cooldown_variation = macro_data.get("cooldown_variation", "fixed")
        self.cooldown_variation_var.set(VARIATION_LABELS_BY_VALUE.get(cooldown_variation, VARIATION_LABELS[0]))
        self._clear_action_selection(log_result=False)
        self._sync_key_input_state()

    def _on_action_selection_changed(self, *_args: object) -> None:
        """Carga en el editor la acción seleccionada sin bloquear la UI."""
        if self.is_loading_action_selection or not hasattr(self, "actions_list_frame"):
            return

        selected_index = self._get_selected_action_index()
        if selected_index is None:
            self._sync_action_buttons_state()
            return

        self._load_action_into_editor(self.actions[selected_index - 1])
        self._sync_action_buttons_state()
        self._set_status(f"Estado: acción {selected_index} seleccionada para edición")

    def _load_action_into_editor(self, action: dict[str, Any]) -> None:
        """Copia tecla, delay y variación de una acción existente al constructor."""
        normalized_key = normalize_key(action.get("key"))
        key_display_name = get_key_display_name(normalized_key)

        if key_display_name in self.simple_key_options:
            self.key_selection_mode_var.set("simple")
            self.simple_key_var.set(str(key_display_name))
            self.advanced_key_var.set(str(normalized_key or "enter"))
        else:
            self.key_selection_mode_var.set("advanced")
            self.advanced_key_var.set(str(normalized_key or action.get("key", "")))

        self.action_delay_var.set(str(float(action.get("base_delay", 0.0))))
        variation = action.get("variation_mode", "fixed")
        self.action_variation_var.set(VARIATION_LABELS_BY_VALUE.get(variation, VARIATION_LABELS[0]))
        self._sync_key_input_state()

    def _reset_action_editor_for_new_action(self) -> None:
        """Deja el editor en un estado predecible para agregar una acción nueva."""
        self.key_selection_mode_var.set("simple")
        self.simple_key_var.set(self.simple_key_options[0])
        self.advanced_key_var.set("enter")
        self.action_delay_var.set("1.0")
        self.action_variation_var.set(VARIATION_LABELS_BY_VALUE["fixed"])
        self._sync_key_input_state()

    def _add_action(self) -> None:
        """Valida controles de acción, agrega la acción y refresca lista/preview."""
        if self._is_runner_active():
            self._show_error("No se pueden agregar acciones mientras la prueba está activa.")
            return

        try:
            action = self._build_action_from_controls()
        except ValueError as error:
            self._show_error(str(error))
            return

        self.actions.append(action)
        self._select_action_index(len(self.actions))
        self._render_actions_list()
        self._append_log_line(
            f"Acción agregada: {self._get_action_display_text(action, len(self.actions))}."
        )
        self._set_status("Estado: acción agregada al constructor")
        self._render_preview()

    def _build_action_from_controls(self) -> dict[str, Any]:
        """Construye una acción normalizada desde el modo de tecla activo."""
        mode = self.key_selection_mode_var.get()
        if mode not in KEY_SELECTION_MODES:
            raise ValueError("El modo de selección de tecla debe ser simple o avanzado.")

        raw_key = self.simple_key_var.get() if mode == "simple" else self.advanced_key_var.get()
        if not validate_key(raw_key):
            raise ValueError("La tecla indicada no es válida para esta fase.")

        normalized_key = normalize_key(raw_key)
        if normalized_key is None:
            raise ValueError("No se pudo normalizar la tecla indicada.")

        return {
            "key": normalized_key,
            "base_delay": self._parse_non_negative_float(self.action_delay_var.get(), "espera base"),
            "variation_mode": self._get_variation_value(self.action_variation_var.get()),
        }

    def _update_selected_action(self) -> None:
        """Reemplaza la acción seleccionada usando los valores actuales del editor."""
        if self._is_runner_active():
            self._show_error("No se pueden actualizar acciones mientras la prueba está activa.")
            return

        selected_index = self._get_selected_action_index()
        if selected_index is None:
            self._show_error("Selecciona una acción antes de presionar 'Actualizar acción'.")
            return

        try:
            action = self._build_action_from_controls()
        except ValueError as error:
            self._show_error(str(error))
            return

        self.actions[selected_index - 1] = action
        self._select_action_index(selected_index)
        self._render_actions_list()
        self._append_log_line(
            f"Acción {selected_index} actualizada: {self._get_action_display_text(action, selected_index)}."
        )
        self._set_status("Estado: acción actualizada")
        self._render_preview()

    def _clear_action_selection(self, log_result: bool = True) -> None:
        """Quita la selección y prepara controles para agregar sin borrar acciones."""
        self._select_action_index(0, load_controls=False)
        self._reset_action_editor_for_new_action()
        self._render_actions_list()
        if log_result:
            self._append_log_line("Selección limpiada. Los controles están listos para agregar una acción nueva.")
            self._set_status("Estado: selección de acción limpiada")

    def _move_selected_action_up(self) -> None:
        """Mueve la acción seleccionada una posición arriba si es posible."""
        self._move_selected_action(direction=-1)

    def _move_selected_action_down(self) -> None:
        """Mueve la acción seleccionada una posición abajo si es posible."""
        self._move_selected_action(direction=1)

    def _move_selected_action(self, direction: int) -> None:
        """Reordena una acción manteniendo selección y previsualización actualizada."""
        if self._is_runner_active():
            self._show_error("No se pueden reordenar acciones mientras la prueba está activa.")
            return

        selected_index = self._get_selected_action_index()
        if selected_index is None:
            self._show_error("Selecciona una acción antes de cambiar su orden.")
            return

        new_index = selected_index + direction
        if new_index < 1 or new_index > len(self.actions):
            self._append_log_line("La acción seleccionada ya está en el límite de la lista; no se cambió el orden.")
            self._set_status("Estado: orden sin cambios")
            return

        current_position = selected_index - 1
        new_position = new_index - 1
        self.actions[current_position], self.actions[new_position] = (
            self.actions[new_position],
            self.actions[current_position],
        )
        self._select_action_index(new_index)
        self._render_actions_list()
        self._append_log_line(f"Acción movida de posición {selected_index} a {new_index}.")
        self._set_status("Estado: acción reordenada")
        self._render_preview()

    def _duplicate_selected_action(self) -> None:
        """Duplica la acción seleccionada y selecciona la copia recién creada."""
        if self._is_runner_active():
            self._show_error("No se pueden duplicar acciones mientras la prueba está activa.")
            return

        selected_index = self._get_selected_action_index()
        if selected_index is None:
            self._show_error("Selecciona una acción antes de duplicarla.")
            return

        duplicated_action = copy.deepcopy(self.actions[selected_index - 1])
        insert_position = selected_index
        self.actions.insert(insert_position, duplicated_action)
        new_index = insert_position + 1
        self._select_action_index(new_index)
        self._render_actions_list()
        self._append_log_line(f"Acción {selected_index} duplicada en la posición {new_index}.")
        self._set_status("Estado: acción duplicada")
        self._render_preview()

    def _get_selected_action_index(self) -> int | None:
        """Devuelve un índice 1-based válido o ``None`` si no hay selección."""
        selected_index = self.selected_action_index_var.get()
        if 1 <= selected_index <= len(self.actions):
            return selected_index
        return None

    def _select_action_index(self, index: int, load_controls: bool = True) -> None:
        """Actualiza la selección evitando callbacks intermedios no deseados."""
        self.is_loading_action_selection = not load_controls
        try:
            self.selected_action_index_var.set(index)
        finally:
            self.is_loading_action_selection = False

        if load_controls and self._get_selected_action_index() is not None:
            self._load_action_into_editor(self.actions[index - 1])
        self._sync_action_buttons_state()

    def _delete_selected_or_last_action(self) -> None:
        """Elimina la acción seleccionada; si no hay selección, elimina la última."""
        if self._is_runner_active():
            self._show_error("No se pueden eliminar acciones mientras la prueba está activa.")
            return

        if not self.actions:
            self._append_log_line("No hay acciones para eliminar.")
            return

        selected_index = self._get_selected_action_index() or len(self.actions)

        removed_action = self.actions.pop(selected_index - 1)
        next_index = min(selected_index, len(self.actions))
        self._select_action_index(next_index if next_index else 0, load_controls=bool(next_index))
        if not self.actions:
            self._reset_action_editor_for_new_action()
        self._render_actions_list()
        self._append_log_line(
            f"Acción eliminada: {self._get_action_display_text(removed_action, selected_index)}."
        )
        self._set_status("Estado: acción eliminada")
        self._render_preview()

    def _clear_actions(self) -> None:
        """Limpia todas las acciones tras confirmar o registra que no había nada."""
        if self._is_runner_active():
            self._show_error("No se pueden limpiar acciones mientras la prueba está activa.")
            return

        if not self.actions:
            self._append_log_line("La lista de acciones ya estaba vacía.")
            return

        confirmed = messagebox.askyesno(
            "Limpiar acciones",
            "¿Quieres eliminar todas las acciones configuradas en la macro actual?",
        )
        if not confirmed:
            self._append_log_line("Limpieza de acciones cancelada por el usuario.")
            return

        removed_count = len(self.actions)
        self.actions.clear()
        self._select_action_index(0, load_controls=False)
        self._reset_action_editor_for_new_action()
        self._render_actions_list()
        self._append_log_line(f"Se limpiaron {removed_count} acciones del constructor.")
        self._set_status("Estado: acciones limpiadas")
        self._render_preview()

    def _render_actions_list(self) -> None:
        """Dibuja la lista de acciones como filas seleccionables."""
        for child in self.actions_list_frame.winfo_children():
            child.destroy()

        selected_index = self._get_selected_action_index()
        self.action_count_label.configure(text=f"Acciones configuradas: {len(self.actions)}")
        if not self.actions:
            ctk.CTkLabel(
                self.actions_list_frame,
                text="Sin acciones. Agrega al menos una acción para ejecutar una macro.",
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=8, pady=8)
            self._sync_action_buttons_state()
            return

        for index, action in enumerate(self.actions, start=1):
            is_selected = index == selected_index
            row = ctk.CTkRadioButton(
                self.actions_list_frame,
                text=self._get_action_display_text(action, index, is_selected=is_selected),
                value=index,
                variable=self.selected_action_index_var,
                command=lambda action_index=index: self._select_action_index(action_index),
            )
            row.grid(row=index - 1, column=0, sticky="ew", padx=8, pady=3)

        self._sync_action_buttons_state()

    def _get_action_display_text(
        self,
        action: dict[str, Any],
        index: int,
        is_selected: bool = False,
    ) -> str:
        """Devuelve una fila legible para la tabla/lista de acciones."""
        key_display_name = get_key_display_name(action.get("key")) or str(action.get("key"))
        variation = action.get("variation_mode", "fixed")
        variation_label = VARIATION_LABELS_BY_VALUE.get(variation, str(variation))
        base_delay = float(action.get("base_delay", 0.0))
        selection_marker = "▶ " if is_selected else "  "
        return f"{selection_marker}{index}. {key_display_name} | {base_delay:.2f}s | {variation_label} ({variation})"

    def _sync_action_buttons_state(self) -> None:
        """Sincroniza botones de edición con selección, límites y ejecución activa."""
        if not hasattr(self, "update_action_button"):
            return

        is_running = self._is_runner_active()
        has_actions = bool(self.actions)
        selected_index = self._get_selected_action_index()
        has_selection = selected_index is not None
        editable_state = "normal" if not is_running else "disabled"
        selection_state = "normal" if has_selection and not is_running else "disabled"
        any_action_state = "normal" if has_actions and not is_running else "disabled"

        self.add_action_button.configure(state=editable_state)
        self.update_action_button.configure(state=editable_state)
        self.clear_selection_button.configure(state=selection_state)
        self.move_action_up_button.configure(state=selection_state)
        self.move_action_down_button.configure(state=selection_state)
        self.duplicate_action_button.configure(state=selection_state)
        self.delete_action_button.configure(state=any_action_state)
        self.clear_actions_button.configure(state=any_action_state)

    def _render_preview(self) -> None:
        """Genera y muestra la previsualización usando la macro editada actual."""
        try:
            safe_macro = self._build_validated_macro_from_controls()
            preview = build_macro_preview(safe_macro)
        except ValueError as error:
            self._show_error(f"No se pudo previsualizar la macro: {error}")
            return

        self.current_macro = safe_macro
        preview_text = self._format_preview(preview)
        self._replace_textbox_content(self.preview_textbox, preview_text)
        self._set_status("Estado: previsualización generada desde el constructor")
        self._append_log_line("Previsualización generada correctamente desde la macro editada.")

    def _build_validated_macro_from_controls(self) -> dict[str, Any]:
        """Construye la macro completa desde controles y la valida antes de usarla."""
        is_infinite = bool(self.infinite_var.get())
        macro_data = {
            "app": APP_NAME,
            "version": str(self.current_macro.get("version", "1.0")),
            "actions": copy.deepcopy(self.actions),
            "initial_delay": self._parse_non_negative_float(self.initial_delay_var.get(), "delay inicial"),
            "repetitions": self._parse_repetitions_value(is_infinite),
            "infinite": is_infinite,
            "cooldown_base": self._parse_non_negative_float(self.cooldown_base_var.get(), "cooldown base"),
            "cooldown_variation": self._get_variation_value(self.cooldown_variation_var.get()),
            "execution_mode": self._get_selected_execution_mode(),
            "key_selection_mode": self._get_key_selection_mode(),
        }
        return self._get_safe_macro_for_selected_mode(macro_data)

    def _get_safe_macro_for_selected_mode(self, macro_data: dict[str, Any]) -> dict[str, Any]:
        """Valida el modo seleccionado y mantiene bloqueado ``test_keys``."""
        macro_copy = copy.deepcopy(macro_data)
        execution_mode = macro_copy.get("execution_mode")

        if execution_mode in BLOCKED_EXECUTION_MODES:
            raise ValueError("El modo test_keys sigue bloqueado en Fase 22.")

        if execution_mode not in ALLOWED_UI_EXECUTION_MODES:
            raise ValueError("Selecciona test_log o real como modo de ejecución.")

        if not validate_macro_data(macro_copy):
            raise ValueError(
                "La macro no cumple la estructura válida. Revisa acciones, delays, repeticiones y cooldown."
            )

        return macro_copy

    def _get_selected_execution_mode(self) -> str:
        """Devuelve el modo elegido en la UI, usando test_log como respaldo seguro."""
        return EXECUTION_MODE_VALUES_BY_LABEL.get(
            self.execution_mode_var.get(),
            DEFAULT_UI_EXECUTION_MODE,
        )

    def _on_execution_mode_changed(self, *_args: object) -> None:
        """Actualiza textos visibles cuando el usuario cambia test_log/real."""
        if not hasattr(self, "run_button"):
            return

        if self._get_selected_execution_mode() == EXECUTION_MODE_REAL:
            self.run_button.configure(text="Ejecutar macro real")
            self._set_status("Estado: modo real seleccionado; se pedirá confirmación antes de ejecutar")
        else:
            self.run_button.configure(text="Ejecutar prueba solo log")
            self._set_status("Estado: modo test_log seleccionado")

    def _get_key_selection_mode(self) -> str:
        """Devuelve el modo de selección activo, limitado a simple/advanced."""
        mode = self.key_selection_mode_var.get()
        if mode not in KEY_SELECTION_MODES:
            raise ValueError("El modo de selección de tecla debe ser simple o avanzado.")
        return mode

    def _get_variation_value(self, selected_label_or_value: str) -> str:
        """Normaliza etiqueta visible o valor interno de variación."""
        if selected_label_or_value in VARIATION_VALUES_BY_LABEL:
            return VARIATION_VALUES_BY_LABEL[selected_label_or_value]
        if selected_label_or_value in VARIATION_LABELS_BY_VALUE:
            return selected_label_or_value
        raise ValueError("La variación debe ser fixed, light, medium o high.")

    def _parse_non_negative_float(self, value: str, field_name: str) -> float:
        """Convierte un campo numérico a float y rechaza negativos o booleanos textuales."""
        clean_value = value.strip()
        if clean_value.lower() in {"true", "false"}:
            raise ValueError(f"El campo {field_name} debe ser un número mayor o igual a cero.")

        try:
            parsed_value = float(clean_value)
        except ValueError as error:
            raise ValueError(f"El campo {field_name} debe ser un número válido.") from error

        if parsed_value < 0:
            raise ValueError(f"El campo {field_name} no puede ser negativo.")

        return parsed_value

    def _parse_repetitions_value(self, is_infinite: bool) -> int:
        """Devuelve repeticiones válidas, usando 1 como respaldo en modo infinito."""
        clean_value = self.repetitions_var.get().strip()
        if is_infinite and not clean_value:
            return 1

        return self._parse_positive_integer(clean_value, "repeticiones")

    def _parse_positive_integer(self, value: str, field_name: str) -> int:
        """Convierte un campo a entero positivo para repeticiones finitas."""
        clean_value = value.strip()
        if not clean_value.isdigit():
            raise ValueError(f"El campo {field_name} debe ser un entero mayor o igual a 1.")

        parsed_value = int(clean_value)
        if parsed_value < 1:
            raise ValueError(f"El campo {field_name} debe ser mayor o igual a 1.")

        return parsed_value

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
            f"Delay inicial: {format_seconds(preview['initial_delay'])}\n"
            f"Cooldown base: {format_seconds(preview['cooldown_base'])}\n"
            f"Variación cooldown: {preview['cooldown_variation']}\n"
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

    def _start_macro_run(self) -> None:
        """Inicia MacroRunner en test_log o real tras validación y confirmación."""
        if self._is_runner_active():
            self._show_error("Ya hay una prueba en ejecución.")
            return

        try:
            safe_macro = self._build_validated_macro_from_controls()
        except ValueError as error:
            self._show_error(f"No se puede ejecutar la macro: {error}")
            return

        if safe_macro["execution_mode"] == EXECUTION_MODE_REAL and not self._confirm_real_execution():
            self._append_log_line("Ejecución real cancelada por el usuario antes de iniciar.")
            self._set_status("Estado: ejecución real cancelada")
            return

        self.current_macro = safe_macro
        self.current_runner = MacroRunner(
            safe_macro,
            log_callback=self._enqueue_runner_event,
            enable_emergency_listener=True,
        )
        self.runner_thread = threading.Thread(
            target=self._run_macro_safely,
            daemon=True,
            name=f"MacroRunnerUI-{safe_macro['execution_mode']}",
        )
        self.runner_thread.start()

        self._set_running_state(True)
        if safe_macro["execution_mode"] == EXECUTION_MODE_REAL:
            self._append_log_line("Ejecución real iniciada tras confirmación manual.")
        else:
            self._append_log_line("Prueba test_log iniciada con la macro editada.")

    def _confirm_real_execution(self) -> bool:
        """Solicita confirmación explícita antes de presionar teclas reales."""
        return messagebox.askyesno(
            "Confirmar ejecución real",
            "La macro presionará teclas reales de teclado.\n\n"
            "Antes de continuar, coloca el foco en la ventana correcta.\n"
            "Puedes detener con el botón 'Detener ahora' o con F9.\n\n"
            "No uses esta función para evasión, abuso, ocultamiento, bypass "
            "ni ejecución no autorizada.\n\n"
            "¿Quieres iniciar la ejecución real ahora?",
        )

    def _run_macro_safely(self) -> None:
        """Ejecuta el runner y transforma errores en eventos visibles para la UI."""
        runner = self.current_runner
        if runner is None:
            self._enqueue_runner_event({"type": "error", "message": "No hay runner activo", "data": {}})
            return

        try:
            runner.run()
        except Exception as error:  # noqa: BLE001 - el error debe verse en el log.
            self._enqueue_runner_event(
                {
                    "type": "error",
                    "message": f"Error durante la ejecución: {error}",
                    "data": {"error_type": type(error).__name__},
                }
            )
        finally:
            self._enqueue_runner_event(
                {"type": "ui_runner_thread_finished", "message": "Hilo de ejecución finalizado", "data": {}}
            )

    def _stop_runner(self) -> None:
        """Solicita detención visual sin depender de F9."""
        if self.current_runner is None or not self._is_runner_active():
            self._append_log_line("No hay una macro activa para detener.")
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
            self._set_status("Estado: ejecución finalizada")
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

    def _set_running_state(self, is_running: bool) -> None:
        """Habilita/deshabilita controles para evitar ediciones durante ejecución."""
        state = "disabled" if is_running else "normal"
        self.load_template_button.configure(state=state)
        self.preview_button.configure(state=state)
        self.run_button.configure(state=state)
        self.execution_mode_menu.configure(state=state)
        self.add_action_button.configure(state=state)
        self.update_action_button.configure(state="disabled" if is_running else "normal")
        self.clear_selection_button.configure(state="disabled" if is_running else "normal")
        self.move_action_up_button.configure(state="disabled" if is_running else "normal")
        self.move_action_down_button.configure(state="disabled" if is_running else "normal")
        self.duplicate_action_button.configure(state="disabled" if is_running else "normal")
        self.delete_action_button.configure(state=state if self.actions else "disabled")
        self.clear_actions_button.configure(state=state if self.actions else "disabled")
        self.save_macro_button.configure(state=state)
        self.refresh_macros_button.configure(state=state)
        self.import_json_button.configure(state=state)
        self.export_json_button.configure(state=state)
        self.stop_button.configure(state="normal" if is_running else "disabled")

        if is_running:
            self.load_macro_button.configure(state="disabled")
            self.delete_macro_button.configure(state="disabled")
            self.saved_macros_menu.configure(state="disabled")
            mode = self.current_macro.get("execution_mode", DEFAULT_UI_EXECUTION_MODE)
            self._set_status(f"Estado: macro en ejecución ({mode})")
        else:
            self.saved_macros_menu.configure(state="normal")
            self._sync_saved_macro_buttons_state()
            self._sync_key_input_state()

        self._sync_action_buttons_state()

    def _is_runner_active(self) -> bool:
        """Indica si existe un hilo de runner vivo."""
        return self.runner_thread is not None and self.runner_thread.is_alive()

    def _append_log_line(self, text: str) -> None:
        """Agrega una línea al log visual manteniendo el scroll al final."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{text}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def _replace_textbox_content(self, textbox: ctk.CTkTextbox, text: str) -> None:
        """Reemplaza de forma segura el contenido de un textbox de solo lectura."""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")

    def _set_status(self, text: str) -> None:
        """Actualiza el estado visible superior."""
        self.status_label.configure(text=text)

    def _show_error(self, message: str) -> None:
        """Muestra errores en messagebox y también en el log visible."""
        self._append_log_line(f"ERROR: {message}")
        self._set_status("Estado: revisar error")
        messagebox.showerror("Sistema de Macros de V", message)


def run_app() -> None:
    """Inicia la aplicación de escritorio."""
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MacroApp()
    app.mainloop()
