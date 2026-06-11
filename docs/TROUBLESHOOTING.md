# Solución de problemas

Esta guía reúne problemas comunes al probar **Sistema de Macros de V** en la release candidate segura `v0.1.0-rc1`.

Todas las soluciones deben mantener el alcance seguro del proyecto. No resuelvas problemas habilitando ejecución real, `test_keys`, grabación, mouse, clicks ni movimientos.

## 1. La app no abre desde Python

Síntomas posibles:

- PowerShell muestra un error al ejecutar `python main.py`.
- Python indica que no encuentra `main.py`.
- Se abre y se cierra inmediatamente.

Solución recomendada:

1. Confirma que estás en la raíz del proyecto.
2. Ejecuta:

   ```powershell
   python --version
   ```

3. Ejecuta:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Intenta abrir de nuevo:

   ```powershell
   python main.py
   ```

No cambies el modo de ejecución para intentar abrir la app. La app debe seguir limitada a `test_log`.

## 2. Faltan dependencias

Síntomas posibles:

- Error `ModuleNotFoundError`.
- Error indicando que falta `customtkinter`, `pynput` o `PyInstaller`.

Solución recomendada:

1. Abre PowerShell en la raíz del proyecto.
2. Instala dependencias:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Si tienes varios Python instalados, confirma que `python` y `pip` apuntan al mismo entorno:

   ```powershell
   python -m pip --version
   ```

No agregues dependencias nuevas para resolver la release candidate salvo que exista una fase autorizada para ello.

## 3. El `.exe` no abre

Síntomas posibles:

- Doble clic sin ventana visible.
- Mensaje de error de Windows.
- Archivo faltante dentro de la carpeta del artifact.

Solución recomendada:

1. Confirma que descargaste el artifact correcto de `v0.1.0-rc1`.
2. Si venía comprimido, extráelo completamente antes de ejecutar.
3. Ejecuta el `.exe` desde su carpeta, no desde dentro del archivo comprimido.
4. Revisa si Windows muestra una advertencia o bloqueo.
5. Si el problema continúa, prueba abrir la app desde Python para comparar el comportamiento.

No intentes corregir el `.exe` habilitando `real` o `test_keys`; esos modos siguen bloqueados.

## 4. Windows muestra advertencia de seguridad

Windows puede mostrar advertencias al abrir ejecutables descargados de Internet, especialmente si no están firmados.

Solución recomendada:

1. Verifica que el archivo provenga de la pre-release oficial `v0.1.0-rc1` del repositorio.
2. No ejecutes archivos recibidos por canales no confiables.
3. Si decides continuar, hazlo solo después de validar el origen.
4. Si tienes dudas, usa el modo Python desde el código fuente revisado.

La advertencia de Windows no debe resolverse alterando la app para ocultarse, evadir controles o automatizar acciones fuera de alcance.

## 5. No aparece el artifact descargado

Síntomas posibles:

- No encuentras el `.exe` después de descargar.
- El navegador descargó un `.zip` o carpeta con otro nombre.
- El workflow no muestra artifacts disponibles.

Solución recomendada:

1. Revisa la carpeta de descargas del navegador.
2. Si el archivo es `.zip`, extráelo.
3. Revisa la página de la pre-release `v0.1.0-rc1` y confirma que el artifact esté adjunto.
4. Si estás revisando GitHub Actions, confirma que el workflow manual `release-build` terminó correctamente.
5. Si el artifact expiró o no está disponible, reporta el problema usando la plantilla adecuada.

No crees artifacts locales generados en el repositorio para subirlos sin seguir la checklist de release.

## 6. El JSON no importa

Síntomas posibles:

- La app muestra un error al importar.
- La macro no aparece en el constructor.
- El archivo no cumple la estructura esperada.

Solución recomendada:

1. Confirma que el archivo tenga extensión `.json`.
2. Abre el archivo en un editor y verifica que sea JSON válido.
3. Comprueba que incluya acciones con teclas válidas, delays numéricos y modo de variación soportado.
4. Intenta crear una macro pequeña desde la UI, exportarla y usarla como referencia.
5. Si el JSON venía de otra persona, revisa que no contenga campos orientados a `real`, `test_keys`, grabación, mouse, clicks o movimientos.

La importación segura debe mantenerse en `test_log`.

## 7. Una tecla no es válida

Síntomas posibles:

- La app rechaza una acción.
- La previsualización falla por una tecla no reconocida.

Solución recomendada:

1. Usa primero el modo de selección simple.
2. Si usas modo avanzado, escribe una tecla soportada por la app.
3. Evita nombres ambiguos, combinaciones no soportadas o valores vacíos.
4. Prueba con teclas simples como `enter` o `space` para descartar errores de formato.

No agregues captura de teclado ni grabación automática para resolver teclas inválidas; esa funcionalidad está fuera de alcance.

## 8. La previsualización falla

Síntomas posibles:

- Error al presionar **Previsualizar**.
- Duración estimada no disponible.
- La macro no pasa validación.

Solución recomendada:

1. Confirma que la macro tenga al menos una acción.
2. Revisa que cada acción tenga tecla válida.
3. Verifica que los delays sean números válidos y no negativos.
4. Revisa repeticiones, delay inicial y cooldown.
5. Si importaste JSON, prueba construir una macro mínima desde la UI y compara.

No cambies el modo a `real` ni a `test_keys`; la previsualización debe funcionar con `test_log`.

## 9. La prueba solo log no inicia

Síntomas posibles:

- El botón **Ejecutar prueba solo log** muestra un error.
- No aparecen eventos nuevos en el log visible.
- La app indica que ya hay una prueba en ejecución.

Solución recomendada:

1. Previsualiza primero la macro.
2. Revisa que haya acciones válidas.
3. Confirma que no exista otra prueba activa.
4. Si hay una prueba activa, usa **Detener ahora** y espera a que finalice.
5. Revisa el log visible para identificar el mensaje exacto.

La solución correcta no es habilitar ejecución real; la prueba esperada es `test_log`.

## 10. Detener ahora no parece responder

Síntomas posibles:

- Presionas **Detener ahora** y la app tarda en reflejar el cambio.
- El log no muestra finalización inmediata.

Solución recomendada:

1. Revisa el log visible para confirmar que se registró la solicitud de detención.
2. Ten en cuenta que el runner se detiene en puntos seguros.
3. Si la macro tiene delays largos, espera unos segundos.
4. Evita iniciar varias pruebas al mismo tiempo.
5. Si el comportamiento se repite, reporta el caso con pasos reproducibles.

No fuerces una interrupción agregando automatización real o hooks de teclado fuera del alcance seguro.

## 11. Revisar logs visibles en la UI

La UI muestra un panel de log para revisar eventos de uso y de ejecución `test_log`.

Úsalo para confirmar:

- Validaciones realizadas.
- Macros cargadas o importadas.
- Inicio de prueba `test_log`.
- Eventos simulados de la macro.
- Solicitud de **Detener ahora**.
- Errores visibles para reproducir un bug.

Al reportar, copia solo mensajes necesarios y evita incluir datos sensibles, rutas privadas, tokens o información personal.

## 12. Cómo reportar bugs usando las plantillas

Para reportar un problema:

1. Abre la pestaña **Issues** del repositorio.
2. Elige la plantilla adecuada:
   - **Bug report** para errores reproducibles.
   - **Release candidate feedback** para comentarios de revisión manual.
   - **Security report** para riesgos de seguridad que puedan describirse de forma segura.
3. Incluye versión, sistema operativo, forma de ejecución y pasos para reproducir.
4. Adjunta logs o capturas solo si no contienen datos sensibles.
5. Confirma que el reporte respeta los límites seguros.

No abras issues solicitando:

- Habilitar `real`.
- Habilitar `test_keys`.
- Ejecutar teclas reales.
- Grabar macros.
- Capturar teclado para automatización.
- Agregar mouse, clicks o movimientos.
- Evasión, ocultamiento, bypass o ejecución no autorizada.

## 13. Límites seguros que deben mantenerse

Aunque aparezca un problema, la solución no debe introducir comportamiento fuera de alcance.

La release candidate segura debe mantener:

- `real` bloqueado.
- `test_keys` bloqueado.
- Sin ejecución real de teclas.
- Sin grabación.
- Sin captura de teclado para construir acciones.
- Sin mouse.
- Sin clicks.
- Sin movimientos de mouse.
- Sin evasión de restricciones.
- Sin ocultamiento de automatización.

Si una solución requiere romper estos límites, no corresponde a Fase 20.
