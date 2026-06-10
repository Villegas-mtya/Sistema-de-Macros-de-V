"""Almacenamiento JSON de macros para Sistema de Macros de V.

La Fase 4 guarda, carga, importa y exporta macros como archivos ``.json``. Todas
las macros internas viven en la carpeta segura de usuario devuelta por
``get_macros_dir()``; nunca se guardan junto al ejecutable, dentro de
``sys._MEIPASS`` ni dependiendo del directorio actual de ejecución.
"""

from __future__ import annotations

import json
import shutil
from copy import deepcopy
from json import JSONDecodeError
from pathlib import Path
from typing import Any, TypedDict

from app import APP_NAME, APP_VERSION
from app.app_paths import get_macros_dir
from app.validators import validate_macro_data

JSON_EXTENSION = ".json"


class MacroFileInfo(TypedDict):
    """Información mínima para mostrar una macro guardada en UI."""

    name: str
    file_name: str
    path: str


DEFAULT_MACRO_DATA: dict[str, Any] = {
    "app": APP_NAME,
    "version": APP_VERSION,
    "actions": [
        {
            "key": "enter",
            "base_delay": 5.0,
            "variation_mode": "medium",
        }
    ],
    "initial_delay": 5.0,
    "repetitions": 10,
    "infinite": False,
    "cooldown_base": 80.0,
    "cooldown_variation": "light",
    "execution_mode": "real",
    "key_selection_mode": "simple",
}


def get_default_macro_template() -> dict[str, Any]:
    """Devuelve una copia independiente de la plantilla oficial de Fase 4."""
    return deepcopy(DEFAULT_MACRO_DATA)


def get_default_macro_data() -> dict[str, Any]:
    """Alias compatible con fases anteriores para obtener la macro por defecto."""
    return get_default_macro_template()


def save_macro(macro_data: object, file_name: str | Path) -> Path:
    """Valida y guarda una macro en la carpeta interna de macros.

    ``file_name`` es un nombre de archivo, no una ruta. La extensión se normaliza
    a ``.json`` y se rechazan nombres vacíos, rutas absolutas o intentos de
    traversal como ``../macro``.
    """
    _ensure_valid_macro(macro_data)
    target_path = _get_internal_macro_path(file_name)

    with target_path.open("w", encoding="utf-8") as macro_file:
        json.dump(macro_data, macro_file, ensure_ascii=False, indent=2)
        macro_file.write("\n")

    return target_path


def load_macro(file_name: str | Path) -> dict[str, Any]:
    """Carga y valida una macro desde la carpeta interna de macros."""
    macro_path = _get_internal_macro_path(file_name)
    if not macro_path.is_file():
        raise FileNotFoundError(f"No existe la macro interna: {macro_path.name}")

    macro_data = _read_json_file(macro_path)
    _ensure_valid_macro(macro_data)
    return macro_data


def list_saved_macros() -> list[MacroFileInfo]:
    """Devuelve metadatos ordenados de macros ``.json`` internas.

    La lista solo incluye archivos reales dentro de ``get_macros_dir()``. Cada
    elemento trae ``name`` sin extensión, ``file_name`` con extensión y ``path``
    absoluto como texto para que la UI no tenga que reconstruir nombres.
    """
    macros_dir = get_macros_dir()
    macro_files = sorted(
        file_path
        for file_path in macros_dir.glob(f"*{JSON_EXTENSION}")
        if file_path.is_file()
    )
    return [
        {
            "name": file_path.stem,
            "file_name": file_path.name,
            "path": str(file_path.resolve()),
        }
        for file_path in macro_files
    ]


def delete_macro(file_name: str | Path) -> bool:
    """Elimina una macro ``.json`` interna y devuelve ``True`` si se eliminó."""
    macro_path = _get_internal_macro_path(file_name)
    if not macro_path.is_file():
        raise FileNotFoundError(f"No existe la macro interna: {macro_path.name}")

    macro_path.unlink()
    return True


def import_macro(source_path: str | Path) -> Path:
    """Importa una macro JSON externa validada a la carpeta interna de macros.

    Si ya existe un archivo con el mismo nombre, se crea un nombre único agregando
    ``_1``, ``_2`` y así sucesivamente para evitar sobrescrituras accidentales.
    """
    source_file = Path(source_path).expanduser()
    if not source_file.is_file():
        raise FileNotFoundError(f"No existe el archivo a importar: {source_file}")

    if source_file.suffix.lower() != JSON_EXTENSION:
        raise ValueError("Solo se pueden importar archivos .json")

    macro_data = _read_json_file(source_file)
    _ensure_valid_macro(macro_data)

    target_name = _normalize_macro_file_name(source_file.name)
    target_path = _get_unique_internal_path(target_name)
    shutil.copy2(source_file, target_path)
    return target_path


def export_macro(file_name: str | Path, destination_path: str | Path) -> Path:
    """Exporta una macro interna validada a una ruta externa.

    Si ``destination_path`` es una carpeta existente, se usa el mismo nombre del
    archivo interno. Si es una ruta de archivo, se usa ese nombre normalizado a
    ``.json``. La función crea carpetas padre cuando hace falta.
    """
    source_path = _get_internal_macro_path(file_name)
    if not source_path.is_file():
        raise FileNotFoundError(f"No existe la macro interna: {source_path.name}")

    # Cargar primero confirma que el JSON interno sigue siendo válido antes de
    # copiarlo fuera de la carpeta segura de usuario.
    load_macro(source_path.name)

    destination = Path(destination_path).expanduser()
    if destination.exists() and destination.is_dir():
        final_path = destination / source_path.name
    else:
        final_name = _normalize_macro_file_name(destination.name)
        final_parent = destination.parent if destination.parent != Path("") else Path.cwd()
        final_path = final_parent / final_name

    final_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, final_path)
    return final_path.resolve()


def _ensure_valid_macro(macro_data: object) -> None:
    """Lanza un error claro si la macro no cumple la estructura de Fase 4."""
    if not validate_macro_data(macro_data):
        raise ValueError("La macro no cumple la estructura JSON válida de Fase 4")


def _read_json_file(file_path: Path) -> dict[str, Any]:
    """Lee un JSON UTF-8 y convierte errores comunes en mensajes claros."""
    try:
        with file_path.open("r", encoding="utf-8") as macro_file:
            data = json.load(macro_file)
    except JSONDecodeError as error:
        raise ValueError(f"El archivo no contiene JSON válido: {file_path}") from error

    if not isinstance(data, dict):
        raise ValueError("El JSON de macro debe ser un objeto/dict en la raíz")

    return data


def _get_internal_macro_path(file_name: str | Path) -> Path:
    """Construye una ruta segura dentro de la carpeta interna de macros."""
    safe_name = _normalize_macro_file_name(file_name)
    return (get_macros_dir() / safe_name).resolve()


def _normalize_macro_file_name(file_name: str | Path) -> str:
    """Normaliza nombres a ``.json`` y rechaza rutas peligrosas."""
    raw_name = str(file_name).strip()
    if not raw_name:
        raise ValueError("El nombre de la macro no puede estar vacío")

    candidate_path = Path(raw_name)
    if candidate_path.is_absolute():
        raise ValueError("El nombre de la macro no puede ser una ruta absoluta")

    if any(separator in raw_name for separator in ("/", "\\")):
        raise ValueError("El nombre de la macro no puede incluir carpetas")

    if raw_name in {".", ".."} or ".." in candidate_path.parts:
        raise ValueError("El nombre de la macro no puede contener traversal")

    normalized_path = candidate_path.with_suffix(JSON_EXTENSION)
    normalized_name = normalized_path.name
    if not normalized_path.stem or normalized_name in {JSON_EXTENSION, f".{JSON_EXTENSION}"}:
        raise ValueError("El nombre de la macro debe incluir un nombre válido")

    return normalized_name


def _get_unique_internal_path(file_name: str | Path) -> Path:
    """Devuelve una ruta interna libre sin sobrescribir archivos existentes."""
    safe_name = _normalize_macro_file_name(file_name)
    macros_dir = get_macros_dir()
    candidate_path = macros_dir / safe_name

    if not candidate_path.exists():
        return candidate_path.resolve()

    base_name = candidate_path.stem
    extension = candidate_path.suffix
    counter = 1

    while True:
        unique_path = macros_dir / f"{base_name}_{counter}{extension}"
        if not unique_path.exists():
            return unique_path.resolve()
        counter += 1
