"""Punto de entrada de Sistema de Macros de V.

Este archivo mantiene el arranque de la aplicación separado de la interfaz para
que las siguientes fases puedan ampliar la UI sin mezclar responsabilidades.
"""

from app.ui import run_app


if __name__ == "__main__":
    run_app()
