"""Pruebas de regresión para almacenamiento JSON de macros."""

from __future__ import annotations

import copy
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.macro_storage import (
    delete_macro,
    export_macro,
    import_macro,
    list_saved_macros,
    load_macro,
    save_macro,
)


VALID_MACRO = {
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


class MacroStorageTests(unittest.TestCase):
    """Aísla los archivos de prueba en un APPDATA temporal y los limpia al salir."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.appdata_path = Path(self.temporary_directory.name)
        self.environment_patch = patch.dict(os.environ, {"APPDATA": str(self.appdata_path)})
        self.environment_patch.start()
        self.addCleanup(self.environment_patch.stop)

    def test_save_load_list_and_delete_macro(self) -> None:
        file_name = "prueba_unittest_storage"
        macro = copy.deepcopy(VALID_MACRO)

        saved_path = save_macro(macro, file_name)
        self.assertTrue(saved_path.is_file())

        loaded_macro = load_macro(f"{file_name}.json")
        saved_macros = list_saved_macros()
        deleted = delete_macro(f"{file_name}.json")

        self.assertEqual(loaded_macro, macro)
        self.assertTrue(any(item["file_name"] == f"{file_name}.json" for item in saved_macros))
        self.assertTrue(deleted)
        self.assertFalse(saved_path.exists())

    def test_export_macro(self) -> None:
        file_name = "prueba_unittest_export"
        macro = copy.deepcopy(VALID_MACRO)
        save_macro(macro, file_name)
        export_directory = self.appdata_path / "exports"
        export_directory.mkdir(parents=True, exist_ok=True)

        exported_path = export_macro(f"{file_name}.json", export_directory)

        self.assertTrue(exported_path.is_file())
        self.assertEqual(exported_path.name, f"{file_name}.json")
        self.assertEqual(load_macro(f"{file_name}.json"), macro)

    def test_import_macro(self) -> None:
        source_name = "prueba_unittest_import.json"
        macro = copy.deepcopy(VALID_MACRO)
        external_directory = self.appdata_path / "external"
        external_directory.mkdir(parents=True, exist_ok=True)
        external_path = external_directory / source_name
        save_macro(macro, "prueba_unittest_storage")
        export_macro("prueba_unittest_storage.json", external_path)
        delete_macro("prueba_unittest_storage.json")

        imported_path = import_macro(external_path)
        loaded_macro = load_macro(source_name)

        self.assertTrue(imported_path.is_file())
        self.assertEqual(imported_path.name, source_name)
        self.assertEqual(loaded_macro, macro)


if __name__ == "__main__":
    unittest.main()
