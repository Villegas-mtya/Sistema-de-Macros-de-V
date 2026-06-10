# Checklist de release candidate segura

Esta checklist valida una versión candidata de **Sistema de Macros de V** sin cambiar el comportamiento funcional de la app. La release candidate de Fase 15 debe conservar solo `execution_mode = "test_log"` y mantener bloqueados `real` y `test_keys`.

> Marca cada punto manualmente antes de etiquetar, publicar o distribuir un build.

## 1. Estado del repositorio

- [ ] Confirmar que se trabaja sobre la rama esperada.
- [ ] Confirmar estado limpio de Git antes del build final.

```powershell
git status --short --branch
```

- [ ] Confirmar que no se agregaron artefactos generados al repositorio:
  - `build/`
  - `dist/`
  - `*.spec`
  - `*.exe`
  - íconos falsos como `app_icon.ico` sin diseño real aprobado

## 2. Dependencias

- [ ] Instalar dependencias desde el archivo versionado.

```powershell
python -m pip install -r requirements.txt
```

- [ ] Confirmar que no se agregaron dependencias nuevas para Fase 15.
- [ ] Confirmar que `requirements.txt` no cambió salvo justificación explícita.

## 3. Validaciones automáticas locales

- [ ] Compilar módulos de la app.

```powershell
python -m compileall app
```

- [ ] Ejecutar pruebas unitarias.

```powershell
python -m unittest discover -s tests
```

- [ ] Ejecutar verificación estática de seguridad.

```powershell
python -c "from pathlib import Path; text=Path('app/ui.py').read_text(encoding='utf-8') + Path('app/macro_runner.py').read_text(encoding='utf-8'); forbidden=['Controller(', '.press(', '.release(']; print(all(item not in text for item in forbidden))"
```

- [ ] Confirmar que la verificación estática imprime `True`.

## 4. CI en GitHub Actions

- [ ] Confirmar que `.github/workflows/ci.yml` existe.
- [ ] Confirmar que el CI se ejecuta en `push` y `pull_request`.
- [ ] Confirmar que el CI instala dependencias, ejecuta `compileall`, ejecuta `unittest` y ejecuta la verificación estática de seguridad.
- [ ] Confirmar que el último workflow de la rama está en verde antes de publicar la release candidate.

## 5. QA manual desde Python

- [ ] Abrir la app desde PowerShell.

```powershell
python main.py
```

- [ ] Confirmar que la ventana abre sin errores visibles.
- [ ] Confirmar que el constructor manual está disponible.
- [ ] Crear una acción en modo simple.
- [ ] Crear una acción en modo avanzado con una tecla soportada.
- [ ] Editar una acción existente.
- [ ] Duplicar una acción existente.
- [ ] Reordenar acciones hacia arriba y hacia abajo.
- [ ] Eliminar una acción.
- [ ] Limpiar selección sin romper el formulario.
- [ ] Configurar delay inicial, repeticiones, cooldown base y variación de cooldown.
- [ ] Probar repetición finita.
- [ ] Probar que la opción visual de repetición infinita no ejecuta teclas reales.

## 6. QA manual de almacenamiento

- [ ] Guardar una macro desde la UI.
- [ ] Cargar una macro guardada desde la UI.
- [ ] Eliminar una macro guardada desde la UI.
- [ ] Importar un archivo JSON válido.
- [ ] Exportar una macro a JSON.
- [ ] Confirmar que una macro cargada o importada queda en `execution_mode = "test_log"`.
- [ ] Confirmar que importar JSON no habilita `real` ni `test_keys`.

## 7. QA manual de previsualización

- [ ] Presionar **Previsualizar** con una macro válida.
- [ ] Confirmar que se muestra número de acciones.
- [ ] Confirmar que se muestra duración estimada.
- [ ] Confirmar que se muestra `execution_mode = test_log`.
- [ ] Confirmar que la previsualización no ejecuta teclas reales.

## 8. QA manual de ejecución segura

- [ ] Presionar **Ejecutar prueba solo log** con una macro válida.
- [ ] Confirmar que aparecen eventos en el log visible.
- [ ] Confirmar que los eventos describen simulación, no pulsaciones reales.
- [ ] Confirmar que no se presionan teclas reales durante la prueba.
- [ ] Presionar **Detener ahora** durante un delay.
- [ ] Confirmar que la ejecución se detiene en un punto seguro.
- [ ] Confirmar que **Detener ahora** no depende de presionar F9 físicamente.

## 9. Build con PyInstaller

- [ ] Ejecutar el build desde PowerShell en Windows.

```powershell
.\build.bat
```

- [ ] Confirmar que el ejecutable existe en la ruta esperada.

```powershell
Test-Path "dist\Sistema de Macros de V\Sistema de Macros de V.exe"
```

- [ ] Confirmar que el comando anterior devuelve `True`.
- [ ] Confirmar que no se agregó `build/`, `dist/`, `*.spec` ni `*.exe` al control de versiones.

## 10. Build manual en GitHub Actions

- [ ] Abrir GitHub Actions en el repositorio.
- [ ] Ejecutar manualmente el workflow **Build manual de release candidate** (`release-build.yml`) con **Run workflow**.
- [ ] Confirmar que el workflow corre sobre `windows-latest` y configura Python 3.11.
- [ ] Confirmar que el workflow termina en verde.
- [ ] Confirmar que antes del build ejecutó `compileall`, `unittest` y la verificación estática de seguridad.
- [ ] Confirmar que el workflow ejecutó `build.bat`.
- [ ] Confirmar que el workflow no ejecutó el `.exe`, no abrió la UI y no ejecutó `python main.py`.
- [ ] Confirmar que el workflow no publicó un GitHub Release y no creó tags automáticamente.
- [ ] Descargar el artifact **Sistema-de-Macros-de-V-release-candidate**.
- [ ] Confirmar que el artifact contiene la carpeta generada `Sistema de Macros de V` y el ejecutable `Sistema de Macros de V.exe`.

## 11. QA manual del ejecutable descargado desde artifact

- [ ] Extraer el artifact descargado en una carpeta temporal fuera del repositorio.
- [ ] Abrir manualmente `Sistema de Macros de V.exe` desde la carpeta extraída.
- [ ] Confirmar que la ventana abre sin consola obligatoria.
- [ ] Repetir una prueba corta de constructor manual.
- [ ] Repetir una prueba corta de guardado/carga.
- [ ] Repetir una prueba corta de importación/exportación.
- [ ] Repetir una prueba corta de previsualización.
- [ ] Repetir una prueba corta de ejecución `test_log`.
- [ ] Repetir una prueba corta de **Detener ahora**.
- [ ] Confirmar que el ejecutable descargado sigue solo en `execution_mode = "test_log"`.
- [ ] Confirmar que `execution_mode = "real"` sigue bloqueado.
- [ ] Confirmar que `execution_mode = "test_keys"` sigue bloqueado.

## 12. QA manual del ejecutable local

- [ ] Abrir `dist\Sistema de Macros de V\Sistema de Macros de V.exe`.
- [ ] Confirmar que la ventana abre sin consola obligatoria.
- [ ] Repetir una prueba corta de constructor manual.
- [ ] Repetir una prueba corta de guardado/carga.
- [ ] Repetir una prueba corta de importación/exportación.
- [ ] Repetir una prueba corta de previsualización.
- [ ] Repetir una prueba corta de ejecución `test_log`.
- [ ] Repetir una prueba corta de **Detener ahora**.
- [ ] Confirmar que el ejecutable mantiene los mismos límites de seguridad que `python main.py`.

## 13. Confirmación de límites de seguridad

- [ ] Confirmar que no hay ejecución real de teclas.
- [ ] Confirmar que `execution_mode = "real"` sigue bloqueado.
- [ ] Confirmar que `execution_mode = "test_keys"` sigue bloqueado.
- [ ] Confirmar que no hay grabación de macros.
- [ ] Confirmar que no hay captura de teclado para construir acciones.
- [ ] Confirmar que no hay mouse.
- [ ] Confirmar que no hay clicks.
- [ ] Confirmar que no hay movimientos de mouse.
- [ ] Confirmar que no se agregaron `recorder.py`, `player.py` ni módulos equivalentes de ejecución real.

## 14. Cierre de release candidate

- [ ] Revisar `README.md` y confirmar que documenta Fase 16.
- [ ] Revisar esta checklist y confirmar que todos los puntos aplicables están marcados.
- [ ] Confirmar que el CI está en verde.
- [ ] Confirmar que el workflow manual `release-build` está en verde cuando se use para distribuir artifact.
- [ ] Confirmar que Git está limpio después de limpiar artefactos locales no versionados.

```powershell
git status --short --branch
```

- [ ] Documentar cualquier limitación conocida antes de distribuir la release candidate.

## Pendiente para Fase 17

Fase 17 no está implementada en esta release candidate. Cualquier avance posterior debe tener una especificación nueva y explícita. En particular, no se debe habilitar ejecución real, `test_keys`, grabación, mouse, clicks ni movimientos sin una fase autorizada y controles de seguridad completos.
