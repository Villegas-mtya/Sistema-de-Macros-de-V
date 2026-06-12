# Guía de usuario final

Esta guía explica cómo instalar, abrir y usar **Sistema de Macros de V** en la release candidate segura `v0.1.0-rc1`.

## 1. Qué es Sistema de Macros de V

Sistema de Macros de V es una aplicación de escritorio en Python para construir macros manuales de teclado desde una interfaz gráfica.

La app permite definir una lista de acciones, guardar esa macro en JSON, volver a cargarla, importarla/exportarla, ejecutar una **prueba solo log** sin presionar teclas y, desde Fase 22, ejecutar teclas reales de forma controlada cuando el usuario selecciona `real` y confirma manualmente.

## 2. Estado actual de la release candidate

`v0.1.0-rc1` es una release candidate pública/manual orientada a revisión, feedback y validación segura.

El comportamiento funcional incluye:

- Construcción manual de macros.
- Validación de datos.
- Previsualización declarativa.
- Guardado/carga/importación/exportación de JSON.
- Ejecución segura `test_log`, que escribe eventos en el log visible sin pulsar teclas reales.
- Ejecución real controlada `real`, que presiona teclas reales solo tras selección explícita y confirmación visual.

`test_log` es el modo por defecto/recomendado para probar. `test_keys` sigue bloqueado. No hay grabación, captura de teclado para construir acciones, mouse, clicks ni movimientos.

## 3. Requisitos mínimos

Para usar la app desde Python:

- Windows recomendado para la revisión de la release candidate.
- Python instalado y disponible en PowerShell como `python`.
- Dependencias instaladas desde `requirements.txt`.
- Repositorio descargado o clonado localmente.

Para usar la app desde el `.exe`:

- Windows.
- Artifact Windows descargado desde la pre-release `v0.1.0-rc1` o desde el workflow manual validado.
- Carpeta extraída completa si el artifact se distribuye comprimido.

## 4. Instalación para modo Python

Abre PowerShell en la raíz del proyecto y ejecuta:

```powershell
python -m pip install -r requirements.txt
```

Si el comando falla, revisa que estés en la carpeta donde existe `requirements.txt` y que Python esté instalado correctamente.

## 5. Abrir la app con Python

Desde PowerShell, en la raíz del proyecto:

```powershell
python main.py
```

La ventana debe mostrar el constructor manual, la lista de acciones, los botones de guardado/carga/importación/exportación, la previsualización, el log visible y el selector de modo `test_log`/`real`, la confirmación previa para `real` y los controles de ejecución.

## 6. Abrir la app desde el `.exe`

1. Descarga el artifact Windows de la pre-release `v0.1.0-rc1` o del workflow manual indicado por el proyecto.
2. Si el artifact está comprimido, extráelo antes de ejecutar.
3. Abre la carpeta extraída.
4. Ejecuta `Sistema de Macros de V.exe`.
5. Si Windows muestra una advertencia de seguridad, revisa que el archivo provenga de la release oficial del repositorio antes de continuar.

No es necesario instalar dependencias Python para abrir el `.exe`, porque el ejecutable empaquetado incluye lo necesario para esa revisión manual.

## 7. Flujo recomendado de primer uso

1. Abre la app desde Python o desde el `.exe`.
2. Crea una macro pequeña con una o dos acciones.
3. Usa **Previsualizar** para confirmar acciones, delays y duración estimada.
4. Ejecuta **Ejecutar prueba solo log**.
5. Observa el log visible: debe mostrar eventos de simulación, no pulsaciones reales.
6. Prueba **Detener ahora** durante una espera larga.
7. Guarda la macro.
8. Cárgala de nuevo para confirmar que se conserva el contenido.
9. Exporta el JSON si quieres revisarlo o compartirlo en un reporte.

## 8. Crear una macro manualmente

La macro se construye desde la UI agregando acciones una por una.

Configura primero los datos generales:

- Nombre de la macro si la UI lo solicita.
- Delay inicial.
- Repeticiones o repetición infinita, según el caso de prueba.
- Cooldown base entre repeticiones.
- Variación de cooldown.

La app fuerza el modo de ejecución seguro `test_log` para las macros creadas, cargadas o importadas desde la UI.

## 9. Agregar una acción

1. Elige el modo de selección de tecla:
   - **Simple**: usa una tecla de la lista disponible.
   - **Avanzado**: escribe una tecla soportada manualmente.
2. Indica la tecla.
3. Define la espera base de la acción.
4. Elige el modo de variación.
5. Presiona **Agregar acción**.
6. Confirma que la acción aparece en la lista visual.

Si la tecla no es válida, la app debe mostrar un error y no agregar la acción.

## 10. Editar una acción

1. Selecciona una acción existente en la lista visual.
2. Revisa que sus datos se carguen en el editor.
3. Cambia la tecla, espera o variación.
4. Presiona **Actualizar acción**.
5. Usa **Previsualizar** para confirmar que el cambio quedó aplicado.

## 11. Duplicar una acción

1. Selecciona la acción que quieres copiar.
2. Presiona **Duplicar acción**.
3. La copia debe insertarse junto a la acción original.
4. Edita la copia si necesitas cambiar tecla, delay o variación.

Duplicar una acción no ejecuta teclas reales; solo modifica la lista declarativa de la macro.

## 12. Reordenar acciones

1. Selecciona una acción en la lista.
2. Usa **Subir acción** para moverla hacia arriba.
3. Usa **Bajar acción** para moverla hacia abajo.
4. Previsualiza para confirmar el orden final.

El orden de la lista es el orden que se recorre durante la prueba `test_log`.

## 13. Eliminar acciones

Para eliminar una acción:

1. Selecciona la acción en la lista.
2. Presiona **Eliminar acción**.
3. Confirma que ya no aparece en la lista.

Si necesitas empezar de nuevo, usa la opción de limpiar acciones solo si estás seguro de descartar la lista actual.

## 14. Guardar una macro

1. Construye o edita la macro.
2. Presiona **Guardar macro**.
3. La app valida la estructura.
4. Si la macro es válida, se guarda como JSON en la carpeta de usuario configurada por la aplicación.

Las macros guardadas deben conservar `execution_mode = "test_log"`.

## 15. Cargar una macro

1. Revisa la lista de macros guardadas.
2. Selecciona una macro.
3. Presiona **Cargar macro**.
4. Confirma que sus acciones y configuración aparecen en el constructor.

Si una macro cargada tuviera otro modo, la UI debe forzarla visualmente a `test_log` antes de usarla.

## 16. Importar JSON

1. Presiona **Importar JSON**.
2. Selecciona un archivo `.json` válido.
3. La app valida la estructura.
4. Si el JSON es válido, se carga en el constructor en modo seguro `test_log`.

Importar JSON carga la macro en `test_log` por seguridad. Para usar `real`, cámbialo manualmente en la UI y acepta la confirmación. `test_keys` y la grabación siguen bloqueados.

## 17. Exportar JSON

1. Selecciona una macro guardada o prepara la macro actual.
2. Presiona **Exportar JSON**.
3. Elige la ubicación de destino.
4. Revisa el archivo exportado si necesitas adjuntarlo a un reporte.

El JSON exportado sirve para revisión, respaldo o reproducción de bugs. No es un ejecutable.

## 18. Previsualizar

Usa **Previsualizar** antes de ejecutar una prueba.

La previsualización ayuda a revisar:

- Modo de ejecución.
- Cantidad de acciones.
- Orden de acciones.
- Teclas declaradas.
- Delays y variaciones.
- Repeticiones.
- Duración estimada.

Si la previsualización falla, revisa que la macro tenga acciones válidas y campos numéricos correctos.

## 19. Ejecutar prueba solo log

Usa **Ejecutar prueba solo log** para recorrer la macro en modo seguro.

Durante esta prueba:

- La app recorre la macro validada.
- Se respetan delays y repeticiones declaradas.
- Se escriben eventos en el log visible.
- No se presionan teclas reales.
- No se habilita `test_keys`.
- No se habilita modo `real`.

## 20. Usar Detener ahora

El botón **Detener ahora** solicita que el runner se detenga de forma segura.

Uso recomendado:

1. Crea una macro con una espera suficientemente larga para poder observarla.
2. Inicia **Ejecutar prueba solo log**.
3. Presiona **Detener ahora**.
4. Revisa el log visible para confirmar que la detención fue solicitada.

La detención puede ocurrir en el siguiente punto seguro del runner; no debe interpretarse como una interrupción violenta del proceso.

## 21. Qué significa `test_log`

`test_log` significa que la app simula el recorrido de la macro y registra eventos en el log visible.

En `test_log`:

- Se valida la macro.
- Se recorren acciones y repeticiones.
- Se esperan los delays configurados.
- Se muestran mensajes de estado.
- No hay pulsación real de teclas.

Este modo existe para revisar la lógica de la macro sin automatizar el sistema operativo ni otras aplicaciones.

## 22. Qué NO hace la app

La release candidate segura no hace lo siguiente:

- No ejecuta teclas reales.
- No habilita modo `real`.
- No habilita `test_keys`.
- No graba macros.
- No captura teclado para construir acciones automáticamente.
- No controla mouse.
- No hace clicks.
- No mueve el mouse.
- No evade restricciones de aplicaciones, juegos, sistemas operativos o servicios.
- No oculta automatización.
- No crea tags, releases ni artifacts automáticamente.

Si necesitas reportar un problema, usa las plantillas del repositorio y mantén el reporte dentro de estos límites seguros.


## Ejecución real segura en Fase 22

1. Primero prueba la macro en **Prueba solo log / `test_log`** y revisa el orden, delays, repeticiones y cooldown en el log.
2. Si el resultado es correcto, cambia el selector a **Ejecución real / `real`**.
3. Coloca el foco en la ventana que debe recibir las teclas.
4. Pulsa el botón de ejecución y lee la confirmación completa.
5. Acepta solo si entiendes que se presionarán teclas reales.
6. Durante la ejecución puedes usar **Detener ahora** o F9.

No uses el modo real para evasión, abuso, ocultamiento, bypass ni ejecución no autorizada.
