# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

## Unreleased

### Fase 22

- Agregada ejecución real controlada de teclado con `execution_mode = "real"`, usando `pynput.keyboard.Controller` solo dentro del runner y solo cuando el usuario selecciona explícitamente ese modo.
- Agregado selector visual de modo `test_log` / `real` en la UI; `test_log` sigue siendo el modo por defecto para probar sin presionar teclas.
- Agregada confirmación manual previa para modo real, con advertencias sobre foco de ventana, parada con **Detener ahora** o F9, y prohibición de evasión, abuso o ejecución no autorizada.
- Agregadas pruebas unitarias con controlador falso para verificar `press`/`release` sin presionar teclas reales durante tests.
- Actualizadas pruebas estáticas para permitir `Controller`, `.press()` y `.release()` únicamente en `app/macro_runner.py`, manteniéndolos fuera de la UI y de módulos no autorizados.
- `test_keys` sigue bloqueado/no implementado. No se agrega grabación, captura de teclado para construir acciones, mouse, clicks ni movimientos.

### Mantenimiento

- Agregado `ROADMAP.md` con el estado público del proyecto, fases completadas, pendientes seguros, fuera del alcance, límites de seguridad y criterios para futuras fases.
- Actualizado `README.md` con enlace al roadmap y resumen de Fase 21.
- Fase 21 quedó como base documental previa; Fase 22 cambia el comportamiento solo para permitir ejecución real controlada de teclado con confirmación explícita.
- Agregado `docs/USER_GUIDE.md` con guía de usuario final, primer uso, uso desde Python, uso desde `.exe`, operaciones de macros y límites de `test_log`.
- Agregado `docs/TROUBLESHOOTING.md` con solución de problemas frecuentes para dependencias, apertura, artifact, JSON, previsualización, prueba solo log, **Detener ahora** y reportes.
- Actualizado `README.md` con enlaces a la documentación de usuario final, solución de problemas, seguridad, changelog y checklist de release candidate.
- Corregidas referencias documentales obsoletas sobre Fase 19 pendiente; Fase 19 ya está integrada.
- Fase 20 se conserva como antecedente documental: en esa fase la aplicación seguía limitada a `test_log`; Fase 22 habilita únicamente `real` controlado y mantiene fuera `test_keys`, grabación, mouse, clicks y movimientos.
- Agregado `SECURITY.md` con la política de seguridad, versiones soportadas y límites para reportes.
- Agregadas plantillas de issues para bugs, feedback de release candidate y reportes de seguridad.
- Agregada plantilla de pull request con checklist de alcance seguro y validaciones locales.
- La ejecución real de teclado queda limitada a Fase 22; `test_keys`, grabación, mouse, clicks y movimientos siguen fuera de alcance.

## v0.1.0-rc1

Release candidate pública y segura preparada para revisión manual. Esta versión candidata no cambia el comportamiento funcional de la aplicación: mantiene el proyecto en modo seguro, con ejecución limitada a `test_log`, y sirve como punto de distribución manual para validar el estado actual antes de avanzar a fases posteriores.

### Incluye

- Constructor manual de macros desde la UI, sin grabación automática ni captura de teclado para generar acciones.
- Creación de acciones con selección de tecla simple o avanzada, espera base y modo de variación.
- Edición de acciones existentes desde la lista visual.
- Reordenamiento de acciones hacia arriba y hacia abajo.
- Duplicación y eliminación de acciones.
- Guardado y carga de macros en formato JSON.
- Importación y exportación manual de macros JSON para revisión o respaldo.
- Previsualización declarativa de la macro antes de ejecutarla, incluyendo cantidad de acciones, repeticiones, delays y duración estimada.
- Ejecución segura `test_log`, que recorre la macro y escribe eventos en el log sin presionar teclas reales.
- Botón **Detener ahora** para solicitar la parada segura del runner durante una ejecución de prueba.
- Parada de emergencia F9 limitada al runner seguro y sin habilitar ejecución real.
- Build local con PyInstaller mediante `build.bat` para generar un ejecutable Windows revisable manualmente.
- CI automático en GitHub Actions con validaciones de compilación, pruebas `unittest` y verificación estática de seguridad.
- Workflow manual `release-build` para generar un artifact descargable de release candidate.
- Límites de seguridad documentados para impedir que la release candidate se interprete como una versión con automatización o ejecución real.

### Límites de seguridad

Esta release candidate mantiene bloqueado todo comportamiento fuera del modo seguro. En particular, **no incluye**:

- Ejecución real de teclas.
- Modo real.
- `test_keys`.
- Grabación de macros.
- Captura de teclado para construir acciones.
- Mouse.
- Clicks.
- Movimientos de mouse.
- Publicación automática de releases.
- Creación automática de tags.

### Publicación manual sugerida

La publicación de `v0.1.0-rc1` debe hacerse manualmente después de confirmar que el CI automático está en verde, que el workflow manual `release-build` generó un artifact válido y que el artifact fue descargado y probado. Los comandos de tag sugeridos son documentales y no deben ejecutarse automáticamente por ningún workflow:

```powershell
git status
git tag -a v0.1.0-rc1 -m "Release candidate v0.1.0-rc1"
git push origin v0.1.0-rc1
```

Después de subir el tag manualmente, crear la GitHub Release desde la interfaz web, marcarla como pre-release si corresponde y adjuntar manualmente el artifact descargado desde `release-build`.
