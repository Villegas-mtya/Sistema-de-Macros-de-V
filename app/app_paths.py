"""Rutas seguras para Sistema de Macros de V.

Este módulo separa dos tipos de rutas:

1. Datos del usuario: macros, logs y configuración. Siempre viven fuera del
   ejecutable y fuera de ``sys._MEIPASS`` para no perderse al empaquetar con
   PyInstaller.
2. Recursos internos: assets incluidos con la aplicación. Se resuelven con
   ``resource_path()`` y pueden vivir dentro de ``sys._MEIPASS`` cuando la app
   está empaquetada.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from app import APP_NAME, APP_VERSION, USER_DATA_DIR_NAME

MACROS_DIR_NAME = "macros"
LOGS_DIR_NAME = "logs"
CONFIG_DIR_NAME = "config"
USER_DATA_DIR_DESCRIPTION = f"APPDATA/{USER_DATA_DIR_NAME}"


def _create_directory(directory_path: Path) -> Path:
    """Crea una carpeta de forma segura y devuelve siempre un Path absoluto."""
    resolved_path = directory_path.expanduser().resolve()
    resolved_path.mkdir(parents=True, exist_ok=True)
    return resolved_path


def get_user_data_dir() -> Path:
    """Devuelve la carpeta raíz segura para datos del usuario.

    En Windows se usa ``APPDATA`` para obtener una ruta como:
    ``C:\\Users\\USUARIO\\AppData\\Roaming\\SistemaMacrosV``.

    Si ``APPDATA`` no existe, se usa un fallback seguro bajo el home del
    usuario. Esta carpeta es para archivos editables por el usuario y nunca debe
    apuntar al ejecutable ni a ``sys._MEIPASS``.
    """
    appdata_directory = os.environ.get("APPDATA")

    if appdata_directory:
        base_directory = Path(appdata_directory)
    else:
        base_directory = Path.home()

    return _create_directory(base_directory / USER_DATA_DIR_NAME)


def get_macros_dir() -> Path:
    """Devuelve y crea la carpeta donde se guardarán macros del usuario."""
    return _create_directory(get_user_data_dir() / MACROS_DIR_NAME)


def get_logs_dir() -> Path:
    """Devuelve y crea la carpeta donde se guardarán logs de la aplicación."""
    return _create_directory(get_user_data_dir() / LOGS_DIR_NAME)


def get_config_dir() -> Path:
    """Devuelve y crea la carpeta donde se guardará la configuración."""
    return _create_directory(get_user_data_dir() / CONFIG_DIR_NAME)


def resource_path(relative_path: str | Path) -> Path:
    """Devuelve la ruta absoluta de un recurso interno de la aplicación.

    ``resource_path()`` debe usarse para assets incluidos con el programa, por
    ejemplo ``assets`` o ``assets/app_icon.ico``. No debe usarse para macros,
    logs ni configuración del usuario.

    En desarrollo, la base es la raíz del repositorio calculada desde este
    archivo, no desde el directorio actual. En un .exe creado con PyInstaller,
    la base es ``sys._MEIPASS``.
    """
    requested_path = Path(relative_path)

    if requested_path.is_absolute():
        return requested_path.resolve()

    pyinstaller_temp_dir = getattr(sys, "_MEIPASS", None)

    if pyinstaller_temp_dir:
        base_path = Path(pyinstaller_temp_dir)
    else:
        base_path = Path(__file__).resolve().parent.parent

    return (base_path / requested_path).resolve()


__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "USER_DATA_DIR_NAME",
    "MACROS_DIR_NAME",
    "LOGS_DIR_NAME",
    "CONFIG_DIR_NAME",
    "USER_DATA_DIR_DESCRIPTION",
    "get_user_data_dir",
    "get_macros_dir",
    "get_logs_dir",
    "get_config_dir",
    "resource_path",
]
