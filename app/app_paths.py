"""Nombres de rutas oficiales de Sistema de Macros de V.

La creación real de carpetas APPDATA y la compatibilidad completa con PyInstaller
se implementarán en la fase dedicada a rutas seguras.
"""

from app import USER_DATA_DIR_NAME

MACROS_DIR_NAME = "macros"
LOGS_DIR_NAME = "logs"
CONFIG_DIR_NAME = "config"
USER_DATA_DIR_DESCRIPTION = f"APPDATA/{USER_DATA_DIR_NAME}"
