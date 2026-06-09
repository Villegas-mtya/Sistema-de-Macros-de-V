"""Interfaz inicial de Sistema de Macros de V.

Fase 1 crea una ventana mínima y útil para comprobar que CustomTkinter abre la
aplicación con el nombre oficial. Las funciones reales de edición, guardado,
previsualización, ejecución y emergencia se implementarán en fases posteriores.
"""

from __future__ import annotations

import customtkinter as ctk

from app import APP_NAME


class MacroApp(ctk.CTk):
    """Ventana principal inicial de la aplicación."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x720")
        self.minsize(1000, 650)
        self._build_initial_layout()

    def _build_initial_layout(self) -> None:
        """Construye una pantalla base clara sin ejecutar macros todavía."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

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
            text="Fase 1: estructura base creada. La ejecución de macros todavía no está habilitada.",
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 18))

        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=24)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        status_badge = ctk.CTkLabel(
            content,
            text="Pendiente: F9 = Detener ahora se implementará antes de cualquier ejecución real",
            fg_color=("#dbeafe", "#1e3a8a"),
            corner_radius=8,
            padx=14,
            pady=8,
        )
        status_badge.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        message = ctk.CTkTextbox(content, height=260, wrap="word")
        message.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        message.insert(
            "1.0",
            "Estructura inicial lista.\n\n"
            "Esta fase solo prepara el proyecto y una ventana mínima. "
            "No hay grabación, no hay mouse y no se presionan teclas reales.\n\n"
            "La siguiente fase agregará rutas seguras para datos de usuario en APPDATA/SistemaMacrosV.",
        )
        message.configure(state="disabled")


def run_app() -> None:
    """Configura CustomTkinter y abre la ventana principal."""
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MacroApp()
    app.mainloop()
