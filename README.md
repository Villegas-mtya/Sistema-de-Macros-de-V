# Sistema de Macros de V

Sistema de Macros de V será una aplicación de escritorio en Python para construir macros manuales de teclado.

## Alcance actual

El proyecto ya integra las Fases 1 a 14 sobre una base segura y progresiva:

- **Fase 4**: almacenamiento, carga, listado, borrado, importación y exportación de macros en JSON.
- **Fase 5**: previsualización declarativa y estimación de duración antes de ejecutar.
- **Fase 6**: runner de simulación en modo prueba **solo log**.
- **Fase 7**: parada de emergencia F9 y control de detención en el runner.
- **Fase 8**: integración inicial en UI con previsualización, logs visibles y botón **Detener ahora**.
- **Fase 9**: constructor manual de macros en la UI con acciones configurables, configuración básica, previsualización y ejecución `test_log` de la macro editada.
- **Fase 10**: guardado visual, carga visual, eliminación, importación JSON y exportación JSON de macros desde la UI.
- **Fase 11**: edición de acciones existentes, limpieza de selección y reordenamiento visual de acciones sin salir del modo seguro `test_log`.
- **Fase 12**: empaquetado preliminar seguro con PyInstaller para generar un ejecutable Windows sin habilitar ejecución real.
- **Fase 13**: pruebas automatizadas de regresión y seguridad con `unittest`, sin abrir UI ni presionar teclas reales.
- **Fase 14**: CI de regresión y seguridad con GitHub Actions en Windows, sin ejecutar la UI ni el `.exe`.

La aplicación ya puede reconocer teclas en modo simple y avanzado, convertirlas a valores internos estables, validar macros guardables, previsualizar duración, recorrer una macro validada sin presionar teclas reales y mostrar el flujo desde una UI inicial de CustomTkinter.

Por seguridad, la ejecución real de teclas todavía no está implementada. Los modos `real` y `test_keys` se rechazan: Fase 14 sigue permitiendo solo simulaciones `test_log` desde la UI y toda macro cargada o importada se fuerza visualmente a `execution_mode = "test_log"`. El botón **Detener ahora** llama a `runner.stop()` sin depender de F9.

## Lo que esta aplicación no hace

- No graba macros automáticamente ni manualmente.
- No captura teclado para grabar acciones.
- No captura mouse.
- No ejecuta clicks.
- No mueve el mouse.
- No implementará grabación de macros, recorder, mouse, clicks ni movimientos en fases futuras.
- No evade restricciones.
- No lee memoria.
- No interactúa directamente con juegos.
- No ejecuta macros automáticamente al abrir.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```


## Teclas soportadas en Fase 3

La Fase 3 separa dos formas de seleccionar teclas:

- **Modo simple**: la UI puede mostrar una lista ordenada de opciones legibles generada por `get_simple_key_options()`.
- **Modo avanzado**: el usuario puede escribir una tecla manualmente, por ejemplo `enter`, `F12`, `x` o `Flecha arriba`.

Las teclas se normalizan internamente antes de guardarse en JSON. Por ejemplo, `Enter`, `enter` y `ENTER` se convierten en `"enter"`; `Flecha arriba` se convierte en `"up"`; y `A` se convierte en `"a"`.

Teclas especiales soportadas:

- `Enter`
- `Space`
- `Esc` / `Escape`
- `Tab`
- `Shift`
- `Ctrl`
- `Alt`
- `Flecha arriba`
- `Flecha abajo`
- `Flecha izquierda`
- `Flecha derecha`
- `F1` a `F12`

También se soportan letras `A-Z` y números `0-9`. No se aceptan palabras desconocidas, textos vacíos, cadenas con solo espacios ni teclas fuera del conjunto soportado.

Una acción básica conserva esta estructura:

```json
{
  "key": "enter",
  "base_delay": 5.0,
  "variation_mode": "medium"
}
```

La Fase 3 solo validaba y normalizaba teclas; la Fase 4 agrega almacenamiento JSON; la Fase 5 agrega previsualización; la Fase 6 agrega un runner seguro que simula la ejecución únicamente con eventos de log; la Fase 7 agrega parada de emergencia; la Fase 8 integra el flujo básico en la UI; la Fase 9 permite construir macros manualmente desde la interfaz; la Fase 10 agrega guardado, carga, importación y exportación visual; la Fase 11 agrega edición y reordenamiento de acciones existentes sin habilitar ejecución real; la Fase 12 prepara el empaquetado seguro con PyInstaller; y la Fase 13 agrega pruebas automatizadas de regresión y seguridad con `unittest`.

## Rutas de usuario

La aplicación crea automáticamente una carpeta de datos de usuario llamada `SistemaMacrosV`.

En Windows, la ruta esperada es:

```text
C:\Users\USUARIO\AppData\Roaming\SistemaMacrosV
```

Si la variable de entorno `APPDATA` no existe, la aplicación usa un fallback seguro bajo el home del usuario:

```text
Path.home() / "SistemaMacrosV"
```

Dentro de esa carpeta se crean estas subcarpetas:

```text
SistemaMacrosV/
├── macros/
├── logs/
└── config/
```

Uso previsto de cada carpeta:

- `macros/`: aquí se guardarán las macros creadas por el usuario en fases posteriores.
- `logs/`: aquí se guardarán registros de la aplicación en fases posteriores.
- `config/`: aquí se guardará la configuración del usuario en fases posteriores.

Estas rutas se crean con `mkdir(parents=True, exist_ok=True)` para que la creación sea segura e idempotente.

## Recursos internos vs. archivos de usuario

Los recursos internos de la aplicación son archivos incluidos con el programa, por ejemplo assets dentro de `assets/`.

Para localizar recursos internos se usa:

```python
resource_path("assets")
```

`resource_path()` funciona tanto en desarrollo con `python main.py` como dentro de un `.exe` creado con PyInstaller, donde puede resolver recursos desde `sys._MEIPASS`.

Importante: `resource_path()` es solo para assets internos. No debe usarse para macros, logs ni configuración del usuario.

Los archivos de usuario deben usar estas funciones:

- `get_user_data_dir()`
- `get_macros_dir()`
- `get_logs_dir()`
- `get_config_dir()`

Esto evita guardar datos editables junto al ejecutable o dentro de `sys._MEIPASS`.

## Prueba rápida de rutas en PowerShell

```powershell
python -c "from app.app_paths import get_user_data_dir, get_macros_dir, get_logs_dir, get_config_dir, resource_path; print(get_user_data_dir()); print(get_macros_dir()); print(get_logs_dir()); print(get_config_dir()); print(resource_path('assets'))"
```

El resultado debe mostrar rutas absolutas para la carpeta de usuario, sus subcarpetas y la carpeta interna `assets`.


## Pruebas rápidas de teclas en PowerShell

```powershell
python -m compileall app
```

```powershell
python -c "from app.key_mapper import normalize_key, validate_key, get_key_display_name; print(normalize_key('Enter')); print(normalize_key('Flecha arriba')); print(validate_key('F12')); print(validate_key('tecla_invalida')); print(get_key_display_name('enter'))"
```

La segunda prueba debe imprimir valores equivalentes a:

```text
enter
up
True
False
Enter
```

## Dependencias

- customtkinter
- pynput
- pyinstaller

## Ícono de la aplicación

Puedes colocar un archivo llamado `app_icon.ico` dentro de la carpeta `assets/`.

El proyecto funciona aunque ese ícono no exista.

## Fase 12: empaquetado preliminar seguro con PyInstaller

La Fase 12 prepara un ejecutable Windows funcional en modo seguro. No habilita ejecución real, `test_keys`, grabación, mouse, clicks ni movimientos. El ejecutable mantiene el mismo comportamiento de la app Python: solo puede ejecutar simulaciones `test_log` y fuerza las macros cargadas o importadas a `execution_mode = "test_log"`.

### Instalar dependencias

Desde PowerShell o CMD, en la raíz del proyecto:

```powershell
python -m pip install -r requirements.txt
```

Las dependencias mínimas son:

- `customtkinter`
- `pynput`
- `pyinstaller`

### Ejecutar la app en modo Python

```powershell
python main.py
```

### Generar el ejecutable

```powershell
.\build.bat
```

También puede ejecutarse desde CMD:

```bat
build.bat
```

`build.bat` usa PyInstaller con `--onedir`, `--windowed`, `--noconfirm`, `--clean`, recursos `assets` y `examples`, y datos de `customtkinter`. Si existe `assets\app_icon.ico`, lo usa como icono; si no existe, construye sin icono y no falla por esa ausencia.

El ejecutable esperado queda en:

```text
dist\Sistema de Macros de V\Sistema de Macros de V.exe
```

### Verificaciones simples en PowerShell

```powershell
python -m compileall app
```

```powershell
python -c "import customtkinter, pynput, PyInstaller; print('dependencias OK')"
```

```powershell
.\build.bat
```

Después del build, verificar manualmente:

```powershell
Test-Path "dist\Sistema de Macros de V\Sistema de Macros de V.exe"
```

El resultado esperado es `True`.

### Seguridad del ejecutable de Fase 12

- El `.exe` sigue funcionando solo en modo `test_log`.
- `execution_mode = "real"` y `execution_mode = "test_keys"` siguen bloqueados desde la UI.
- No se presionan teclas reales todavía.
- No hay grabación de macros.
- No hay captura de mouse, clicks ni movimientos.
- Fase 12 es solo empaquetado preliminar; Fase 13 agrega pruebas automatizadas sin cambiar estos límites de seguridad.

## Fase 13: pruebas automatizadas de regresión y seguridad

La Fase 13 agrega una suite básica con `unittest` de la librería estándar para proteger el comportamiento ya implementado entre Fase 1 y Fase 12. El propósito es detectar regresiones en mapeo de teclas, validación de macros, previsualización, runner `test_log`, almacenamiento JSON y reglas estáticas de seguridad.

Estas pruebas no abren la UI gráfica, no ejecutan `main.py`, no dependen de `$DISPLAY` y no presionan teclas reales. Los modos `real` y `test_keys` siguen bloqueados: las pruebas verifican que `MacroRunner` los rechace con `ValueError` y que `app/ui.py` y `app/macro_runner.py` no contengan llamadas directas a `Controller(`, `.press(` ni `.release(`.

### Ejecutar pruebas en PowerShell

Desde la raíz del proyecto:

```powershell
python -m compileall app
```

```powershell
python -m unittest discover -s tests
```

```powershell
python -c "from pathlib import Path; text=Path('app/ui.py').read_text(encoding='utf-8') + Path('app/macro_runner.py').read_text(encoding='utf-8'); forbidden=['Controller(', '.press(', '.release(']; print(all(item not in text for item in forbidden))"
```

El último comando debe imprimir `True`. La revisión de la UI gráfica se mantiene manual: ejecutar `python main.py`, comprobar visualmente el constructor, previsualización, guardado/carga e inicio/detención `test_log`, y cerrar la ventana sin habilitar ejecución real.

## Fase 14: CI de regresión y seguridad con GitHub Actions

La Fase 14 agrega el workflow `.github/workflows/ci.yml` para ejecutar automáticamente las validaciones de regresión y seguridad en GitHub Actions. El flujo corre en `windows-latest` para evitar problemas típicos de `pynput` en Linux sin `$DISPLAY` y usa Python 3.11 como versión estable.

El CI se activa en `push` y `pull_request`. Sus pasos son deliberadamente seguros y no cambian el comportamiento de la aplicación:

- Instala dependencias con `python -m pip install --upgrade pip` y `python -m pip install -r requirements.txt`.
- Ejecuta `python -m compileall app` para detectar errores de sintaxis/importación básica en los módulos de la app.
- Ejecuta `python -m unittest discover -s tests` para correr las pruebas automatizadas de Fase 13.
- Ejecuta una verificación estática que revisa que `app/ui.py` y `app/macro_runner.py` no contengan llamadas directas a `Controller(`, `.press(` ni `.release(`.

Límites de seguridad de Fase 14:

- No ejecuta teclas reales.
- No habilita `execution_mode = "real"`.
- No habilita `execution_mode = "test_keys"`.
- No abre la UI automáticamente.
- No ejecuta `python main.py` dentro del CI.
- No ejecuta el `.exe` dentro del CI.
- La revisión de `python main.py` y del ejecutable generado por `build.bat` sigue siendo manual.

Comandos locales equivalentes en PowerShell, desde la raíz del proyecto:

```powershell
python -m compileall app
```

```powershell
python -m unittest discover -s tests
```

```powershell
python -c "from pathlib import Path; text=Path('app/ui.py').read_text(encoding='utf-8') + Path('app/macro_runner.py').read_text(encoding='utf-8'); forbidden=['Controller(', '.press(', '.release(']; print(all(item not in text for item in forbidden))"
```

El último comando debe imprimir `True`. Si cualquiera de estos comandos falla en local o en GitHub Actions, la rama debe corregirse antes de avanzar a fases posteriores.

## Fase 4: almacenamiento JSON de macros

La Fase 4 agrega almacenamiento, carga, importación y exportación de macros en archivos `.json`. Esta fase trabaja solo con datos: no ejecuta macros, no activa F9 global, no captura teclado para grabar acciones y no agrega mouse, clicks ni movimientos. La ejecución simulada solo aparece después, en Fase 6, mediante un runner de logs sin pulsación real de teclas.

### Dónde se guardan las macros

Las macros internas se guardan siempre en la carpeta segura de usuario:

```text
APPDATA/SistemaMacrosV/macros
```

En Windows normalmente equivale a:

```text
C:\Users\USUARIO\AppData\Roaming\SistemaMacrosV\macros
```

El código usa `get_macros_dir()` desde `app/app_paths.py`, por lo que no guarda macros junto al ejecutable, no depende del directorio actual de ejecución y no escribe dentro de `sys._MEIPASS` cuando la aplicación se empaqueta.

### Formato JSON base

Una macro válida de Fase 4 usa esta estructura mínima:

```json
{
  "app": "Sistema de Macros de V",
  "version": "1.0",
  "actions": [
    {
      "key": "enter",
      "base_delay": 5.0,
      "variation_mode": "medium"
    }
  ],
  "initial_delay": 5.0,
  "repetitions": 10,
  "infinite": false,
  "cooldown_base": 80.0,
  "cooldown_variation": "light",
  "execution_mode": "real",
  "key_selection_mode": "simple"
}
```

Campos validados:

- `actions` debe ser una lista.
- Cada acción debe tener `key`, `base_delay` y `variation_mode`.
- `key` debe ser una tecla soportada por `app.key_mapper.validate_key()`.
- `base_delay`, `initial_delay` y `cooldown_base` deben ser números mayores o iguales a cero.
- `variation_mode` y `cooldown_variation` aceptan `fixed`, `light`, `medium` o `high`.
- `infinite` debe ser booleano.
- `repetitions` debe ser entero mayor o igual a 1 cuando `infinite` es `false`.
- `execution_mode` acepta `real`, `test_log` o `test_keys` como valores declarativos para fases posteriores.
- `key_selection_mode` acepta `simple` o `advanced`.

### Importación y exportación

`app/macro_storage.py` expone estas funciones principales:

- `get_default_macro_template()`: devuelve una plantilla nueva y validable.
- `save_macro(macro_data, file_name)`: valida y guarda en `APPDATA/SistemaMacrosV/macros` con extensión `.json`.
- `load_macro(file_name)`: carga y valida una macro interna.
- `list_saved_macros()`: devuelve una lista ordenada de metadatos de macros internas (`name`, `file_name` y `path`).
- `delete_macro(file_name)`: elimina solo macros `.json` internas.
- `import_macro(source_path)`: importa un `.json` externo validado y evita sobrescrituras con nombres únicos.
- `export_macro(file_name, destination_path)`: exporta una macro interna validada a una carpeta o archivo externo.

Los nombres internos de macro rechazan rutas absolutas, carpetas y traversal como `../` para evitar escrituras fuera de la carpeta segura.

### Pruebas rápidas de Fase 4 en PowerShell

```powershell
python -m compileall app
```

```powershell
python -c "from app.macro_storage import get_default_macro_template, save_macro, load_macro, list_saved_macros; data=get_default_macro_template(); path=save_macro(data, 'prueba_fase_4'); print(path); loaded=load_macro('prueba_fase_4'); print(loaded['app']); print(len(list_saved_macros()) >= 1)"
```

```powershell
python -c "from app.validators import validate_macro_data; from app.macro_storage import get_default_macro_template; print(validate_macro_data(get_default_macro_template()))"
```

## Fase 5: previsualización y estimación de duración

La Fase 5 agrega una capa de previsualización de macros antes de cualquier ejecución. Esta fase sigue siendo declarativa: no presiona teclas, no activa F9 global, no implementa el botón **Detener ahora** y no agrega UI completa ni modal gráfico. La Fase 6, documentada más abajo, añade el primer runner seguro, pero solo en modo log.

`app/preview.py` expone funciones para construir un resumen estructurado que una futura interfaz podrá mostrar al usuario:

- `get_variation_seconds(variation_mode)`: devuelve la variación en segundos para `fixed`, `light`, `medium` o `high`.
- `calculate_delay_range(base_delay, variation_mode)`: calcula duración mínima, promedio y máxima de un retardo.
- `estimate_macro_duration(macro_data)`: estima duración total o por ciclo usando una macro validada.
- `format_seconds(seconds)`: convierte segundos a texto legible como `5 s`, `1 min 5 s` o `1 h 1 min 1 s`.
- `build_action_preview(action, index)`: crea el resumen de una acción con tecla legible y rango de delay.
- `build_macro_preview(macro_data)`: crea el resumen completo de la macro, incluyendo acciones, repeticiones, modo de ejecución y `human_summary`.

### Cómo se calcula la variación

Los modos de variación de Fase 5 usan estos valores fijos:

```text
fixed  = 0.00 s
light  = 0.15 s
medium = 0.30 s
high   = 0.50 s
```

Para cada delay con variación se calcula:

```text
mínimo   = max(0, base_delay - variation)
promedio = base_delay
máximo   = base_delay + variation
```

La estimación de duración incluye:

- `initial_delay` una sola vez al inicio.
- Los delays de cada acción en cada repetición.
- `cooldown_base` con variación entre repeticiones finitas, pero no después de la última.
- En macros infinitas, `total` queda como `None` porque la duración total es indefinida, y se informa una referencia por repetición y por ciclo repetible.

### Pruebas rápidas de Fase 5 en PowerShell

```powershell
python -m compileall app
```

```powershell
python -c "from app.macro_storage import get_default_macro_template; from app.preview import build_macro_preview; preview=build_macro_preview(get_default_macro_template()); print(preview['actions_count']); print(preview['duration_estimate']['infinite']); print(preview['actions'][0]['key_display_name'])"
```

```powershell
python -c "from app.preview import format_seconds, calculate_delay_range; print(format_seconds(65)); print(calculate_delay_range(5.0, 'medium'))"
```

## Fase 6: runner en modo prueba solo log

La Fase 6 completa `app/macro_runner.py` con una clase `MacroRunner` para simular el flujo de ejecución de una macro validada sin riesgo. El runner recorre `initial_delay`, acciones, `base_delay` con variación, repeticiones, cooldown entre repeticiones y macros infinitas, pero únicamente genera eventos de log.

Características principales:

- Solo permite `execution_mode = "test_log"`.
- Rechaza `execution_mode = "real"` porque todavía faltan F9 global y controles de emergencia antes de presionar teclas reales.
- Rechaza `execution_mode = "test_keys"` porque también implicaría emitir teclas.
- No usa `pynput.Controller` ni presiona teclas reales.
- Usa `get_key_display_name()` para mostrar teclas legibles en los eventos.
- Acepta `log_callback` para enviar eventos a una UI futura o a pruebas.
- Acepta `stop_callback` y el método `stop()` para solicitar detención en puntos seguros.
- Acepta `sleep_function` inyectable para pruebas rápidas sin esperar segundos reales.
- Puede iniciarse con `run()` de forma síncrona o con `start()` en un hilo daemon para no bloquear una UI futura.

Ejemplo de evento generado:

```python
{
    "type": "action",
    "message": "Simulando tecla Enter",
    "data": {
        "repetition": 1,
        "action_index": 1,
        "key": "enter",
        "key_display_name": "Enter",
    },
}
```

La variación de delays usa los mismos valores aprobados para el proyecto:

```text
fixed  = 0.00 s
light  = 0.15 s
medium = 0.30 s
high   = 0.50 s
```

F9 global, listener global, ejecución real de teclas, botón operativo **Detener ahora** e integración visual con `app/ui.py` quedan documentados como avances posteriores a Fase 6. Desde Fase 8 ya existe integración visual básica, pero el runner sigue limitado a logs y no pulsa teclas reales.

### Pruebas rápidas de Fase 6 en PowerShell

```powershell
python -m compileall app
```

```powershell
python -c "from app.macro_storage import get_default_macro_template; from app.macro_runner import MacroRunner; logs=[]; data=get_default_macro_template(); data['execution_mode']='test_log'; runner=MacroRunner(data, log_callback=logs.append, sleep_function=lambda seconds: None); runner.run(); print(len(logs) > 0); print(logs[0]['type']); print(logs[-1]['type'])"
```

```powershell
python -c "from app.macro_storage import get_default_macro_template; from app.macro_runner import MacroRunner; data=get_default_macro_template(); data['execution_mode']='real'; runner=MacroRunner(data, sleep_function=lambda seconds: None); ok=False;
try:
    runner.run()
except ValueError:
    ok=True
print('real rechazado' if ok else 'ERROR')"
```

## Fase 7: parada de emergencia F9 global

La Fase 7 agrega control seguro de detención al runner sin avanzar a ejecución real. `app/macro_runner.py` sigue limitado a `execution_mode = "test_log"`: los modos `real` y `test_keys` continúan bloqueados porque todavía no existe una fase aprobada para presionar teclas reales.

Características principales:

- `MacroRunner.stop()` permite solicitar detención manual y cerrar la simulación en puntos seguros.
- `MacroRunner.trigger_emergency_stop()` y `MacroRunner.request_emergency_stop()` permiten simular una parada de emergencia en pruebas sin presionar F9 físicamente.
- `EmergencyStopController` puede iniciar y detener un listener global no bloqueante, limitado exclusivamente a `F9`.
- La única escucha global permitida en esta fase es `F9`; cualquier otra tecla se ignora sin guardarse, sin registrarse y sin usarse para acciones.
- F9 solo detiene una simulación en curso: no graba teclas, no captura acciones, no registra pulsaciones y no habilita hotkeys configurables.
- Los delays se revisan en intervalos cortos para detectar `stop()`, parada de emergencia o F9 sin esperar el delay completo.
- Integrado en Fase 8: botón visual **Detener ahora** e integración básica con `app/ui.py`. Pendiente para fases futuras: modal gráfico completo, `test_keys` solo si se autoriza después y ejecución real solo después de controles de seguridad completos.
- Fuera del alcance del proyecto: grabación de macros, captura de teclado para construir acciones, mouse, clicks y movimientos.

Eventos relevantes:

- `emergency_listener_started`: el listener global de F9 se inició.
- `emergency_listener_stopped`: el listener global de F9 se detuvo.
- `emergency_stop_triggered`: se disparó una parada de emergencia.
- `stop_requested`: el runner detectó una solicitud de detención en un punto seguro.
- `macro_stopped`: la macro simulada terminó detenida de forma segura.
- `macro_finished`: la macro simulada terminó normalmente.

Para usar el listener F9 en una integración futura, se debe iniciar explícitamente con `start_emergency_listener()` o crear el runner con `enable_emergency_listener=True`. En entornos sin soporte para listeners globales, las pruebas recomendadas usan `trigger_emergency_stop()` para no depender del teclado físico.

### Pruebas rápidas de Fase 7 en PowerShell

```powershell
python -m compileall app
```

```powershell
python -c "from app.macro_storage import get_default_macro_template; from app.macro_runner import MacroRunner; logs=[]; data=get_default_macro_template(); data['execution_mode']='test_log'; runner=MacroRunner(data, log_callback=logs.append, sleep_function=lambda seconds: None); runner.stop(); runner.run(); print(any(event['type'] in ('stop_requested','macro_stopped') for event in logs)); print(logs[-1]['type'])"
```

```powershell
python -c "from app.macro_storage import get_default_macro_template; from app.macro_runner import MacroRunner; logs=[]; data=get_default_macro_template(); data['execution_mode']='test_log'; runner=MacroRunner(data, log_callback=logs.append, sleep_function=lambda seconds: None); trigger = getattr(runner, 'trigger_emergency_stop', None) or getattr(runner, 'request_emergency_stop', None) or runner.stop; trigger(); runner.run(); print(any(event['type'] in ('emergency_stop_triggered','stop_requested','macro_stopped') for event in logs)); print(logs[-1]['type'])"
```

```powershell
python -c "from pathlib import Path; text=Path('app/macro_runner.py').read_text(encoding='utf-8'); forbidden=['Controller(', '.press(', '.release(']; print(all(item not in text for item in forbidden))"
```


## Fase 8: integración inicial de UI

La Fase 8 actualiza `app/ui.py` para unir visualmente la plantilla de macro, la previsualización declarativa y el runner `test_log` ya implementados. La pantalla principal de CustomTkinter conserva una estructura simple: encabezado, panel de estado, controles, panel de previsualización y log con scroll.

Características principales:

- Botón **Cargar plantilla**: reinicia una macro en memoria usando `get_default_macro_template()` y fuerza `execution_mode = "test_log"` para mantener la fase segura.
- Botón **Previsualizar**: llama a `build_macro_preview()` y muestra número de acciones, repeticiones, si la macro es infinita, modo de ejecución, modo de selección, duración estimada y lista básica de acciones con nombre legible de tecla.
- Botón **Ejecutar prueba solo log**: crea un `MacroRunner` en un hilo separado para que la UI no se congele. Los eventos se envían a una cola y se muestran en el log visible.
- Botón **Detener ahora**: llama a `runner.stop()` y registra en pantalla que se solicitó la detención. No depende de F9.
- Manejo de errores: los errores se muestran en el log y con `messagebox`.

Límites de seguridad de Fase 8:

- No usa `pynput.Controller`.
- No presiona teclas reales.
- No habilita ejecución real de macros.
- No habilita `execution_mode = "real"`.
- No habilita `execution_mode = "test_keys"`.
- No implementa editor completo, grabación, captura de teclado, mouse, clicks, movimientos, `recorder.py`, `player.py`, `duration.py`, `storage.py`, `validation.py` ni estructura `src/`.

### Pruebas rápidas de Fase 8 en PowerShell

Compilar módulos de la aplicación:

```powershell
python -m compileall app
```

Probar plantilla, previsualización y runner `test_log` sin esperar segundos reales:

```powershell
python -c "from app.macro_storage import get_default_macro_template; from app.preview import build_macro_preview; from app.macro_runner import MacroRunner; data=get_default_macro_template(); data['execution_mode']='test_log'; preview=build_macro_preview(data); logs=[]; runner=MacroRunner(data, log_callback=logs.append, sleep_function=lambda seconds: None); runner.run(); print(preview['actions_count']); print(len(logs) > 0); print(logs[-1]['type'])"
```

Abrir la UI de Fase 8:

```powershell
python main.py
```

Flujo manual recomendado en la UI:

1. Presionar **Cargar plantilla**.
2. Presionar **Previsualizar** y revisar acciones/duración.
3. Presionar **Ejecutar prueba solo log**.
4. Confirmar que aparecen eventos como inicio, delay inicial, repetición, acción simulada, cooldown, detención o finalización.
5. Presionar **Detener ahora** durante una espera para comprobar que la simulación se detiene en un punto seguro.

## Fase 9: constructor manual de macros en la UI

La Fase 9 actualiza `app/ui.py` para que la macro ya no dependa únicamente de la plantilla inicial. La pantalla principal conserva encabezado, paneles visuales, estado claro, previsualización, log con scroll, ejecución no bloqueante y botón **Detener ahora**, pero agrega un constructor manual de acciones y configuración básica.

Características principales:

- Sección **Constructor de macro** con modo de selección de tecla **simple** o **avanzado**.
- Modo simple usando las opciones visibles generadas por `get_simple_key_options()`.
- Modo avanzado con entrada manual validada mediante `validate_key()` y normalizada con `normalize_key()`.
- Botón **Agregar acción** para crear acciones con `key`, `base_delay` y `variation_mode`.
- Lista visual de acciones con número, tecla legible, espera base y variación.
- Botón **Eliminar acción** para quitar la acción seleccionada o, si no hay selección válida, la última acción.
- Botón **Limpiar acciones** con confirmación antes de borrar toda la lista.
- Configuración editable de `initial_delay`, `repetitions`, `infinite`, `cooldown_base` y `cooldown_variation`.
- Previsualización con `build_macro_preview()` usando siempre la macro editada desde los controles actuales.
- Ejecución con `MacroRunner` usando la macro editada y forzando `execution_mode = "test_log"`.

Límites de seguridad de Fase 9:

- No hay ejecución real de teclas.
- No se puede seleccionar `execution_mode = "real"`.
- No se puede seleccionar `execution_mode = "test_keys"`.
- No se implementa guardado visual de macros.
- No se implementa importación ni exportación visual.
- No se implementa grabación, captura de teclado para construir acciones, mouse, clicks, movimientos, `recorder.py`, `player.py`, `duration.py`, `storage.py`, `validation.py` ni estructura `src/`.

### Pruebas rápidas de Fase 9 en PowerShell

Compilar módulos de la aplicación:

```powershell
python -m compileall app
```

Validar una macro `test_log` mínima construible por la UI:

```powershell
python -c "from app.validators import validate_macro_data; data={'app':'Sistema de Macros de V','version':'1.0','actions':[{'key':'enter','base_delay':1.0,'variation_mode':'fixed'}],'initial_delay':0.0,'repetitions':1,'infinite':False,'cooldown_base':0.0,'cooldown_variation':'fixed','execution_mode':'test_log','key_selection_mode':'simple'}; print(validate_macro_data(data))"
```

Previsualizar una macro mínima y comprobar acción/tecla legible:

```powershell
python -c "from app.preview import build_macro_preview; data={'app':'Sistema de Macros de V','version':'1.0','actions':[{'key':'enter','base_delay':1.0,'variation_mode':'fixed'}],'initial_delay':0.0,'repetitions':1,'infinite':False,'cooldown_base':0.0,'cooldown_variation':'fixed','execution_mode':'test_log','key_selection_mode':'simple'}; preview=build_macro_preview(data); print(preview['actions_count']); print(preview['actions'][0]['key_display_name'])"
```

Abrir la UI de Fase 9:

```powershell
python main.py
```

Flujo manual recomendado en la UI:

1. Elegir modo **Simple** y una tecla visible, o modo **Avanzado** y escribir una tecla soportada.
2. Configurar espera base y variación de la acción.
3. Presionar **Agregar acción** y revisar la lista visual.
4. Probar **Eliminar acción** o **Limpiar acciones** si necesitas ajustar la lista.
5. Configurar delay inicial, repeticiones, infinito, cooldown base y variación de cooldown.
6. Presionar **Previsualizar** para revisar la macro editada.
7. Presionar **Ejecutar prueba solo log** y confirmar eventos en el log visible.
8. Presionar **Detener ahora** durante una espera para comprobar la detención segura.

## Fase 10: guardado visual e importación/exportación JSON

La Fase 10 actualiza `app/ui.py` para integrar visualmente las funciones de `app/macro_storage.py` con el constructor manual de Fase 9. La pantalla sigue conservando encabezado, constructor de acciones, lista visual, configuración de macro, previsualización, log con scroll, ejecución no bloqueante `test_log` y botón **Detener ahora**.

Características principales:

- Nueva sección **Macros guardadas** dentro de la UI.
- Campo **Nombre de macro** para guardar la macro construida desde los controles actuales.
- Botón **Guardar macro** que construye la macro actual, fuerza `execution_mode = "test_log"`, valida con `validate_macro_data()` y guarda con `save_macro()`.
- Botón **Actualizar lista** que refresca el selector usando `list_saved_macros()`.
- Selector visual de macros guardadas.
- Botón **Cargar macro** que usa `load_macro()`, carga acciones/configuración al constructor y actualiza la previsualización.
- Botón **Eliminar macro** con confirmación y borrado mediante `delete_macro()`.
- Botón **Importar JSON** que abre un selector de archivos `.json`, usa `import_macro()`, actualiza la lista y carga la macro importada al constructor.
- Botón **Exportar JSON** que permite exportar una macro guardada con `export_macro()` o, si no hay selección, exportar la macro actual validada a un archivo JSON externo.

Límites de seguridad de Fase 10:

- Toda macro construida desde la UI usa siempre `execution_mode = "test_log"`.
- Toda macro cargada o importada con `execution_mode = "real"` o `execution_mode = "test_keys"` se convierte en la UI a `execution_mode = "test_log"` y se registra en el log visible.
- No hay ejecución real de teclas.
- Los modos `real` y `test_keys` siguen bloqueados.
- No se implementa grabación, captura de teclado para construir acciones, mouse, clicks, movimientos, `recorder.py`, `player.py`, `duration.py`, `storage.py`, `validation.py` ni estructura `src/`.

### Pruebas rápidas de Fase 10 en PowerShell

Compilar módulos de la aplicación:

```powershell
python -m compileall app
```

Guardar, cargar, listar y eliminar una macro interna:

```powershell
python -c "from app.macro_storage import save_macro, load_macro, list_saved_macros, delete_macro; data={'app':'Sistema de Macros de V','version':'1.0','actions':[{'key':'enter','base_delay':1.0,'variation_mode':'fixed'}],'initial_delay':0.0,'repetitions':1,'infinite':False,'cooldown_base':0.0,'cooldown_variation':'fixed','execution_mode':'test_log','key_selection_mode':'simple'}; path=save_macro(data,'prueba_fase_10'); loaded=load_macro('prueba_fase_10'); print(loaded['execution_mode']); print(any(m['name']=='prueba_fase_10' for m in list_saved_macros())); print(delete_macro('prueba_fase_10'))"
```

Exportar una macro guardada a un JSON temporal:

```powershell
python -c "from pathlib import Path; import tempfile; from app.macro_storage import save_macro, export_macro, delete_macro; data={'app':'Sistema de Macros de V','version':'1.0','actions':[{'key':'enter','base_delay':1.0,'variation_mode':'fixed'}],'initial_delay':0.0,'repetitions':1,'infinite':False,'cooldown_base':0.0,'cooldown_variation':'fixed','execution_mode':'test_log','key_selection_mode':'simple'}; save_macro(data,'prueba_export_fase_10'); dest=Path(tempfile.gettempdir())/'prueba_export_fase_10.json'; export_macro('prueba_export_fase_10', dest); print(dest.exists()); print(delete_macro('prueba_export_fase_10')); dest.unlink(missing_ok=True)"
```

Abrir la UI de Fase 10:

```powershell
python main.py
```

Flujo manual recomendado en la UI:

1. Crear o ajustar acciones desde el constructor manual.
2. Escribir un **Nombre de macro** no vacío.
3. Presionar **Guardar macro** y comprobar el mensaje en el log visible.
4. Presionar **Actualizar lista** si quieres refrescar el selector manualmente.
5. Seleccionar una macro y presionar **Cargar macro** para llevarla al constructor.
6. Probar **Importar JSON** con un archivo válido y confirmar que queda cargado en modo `test_log`.
7. Probar **Exportar JSON** con una macro seleccionada o, si no hay macros guardadas, con la macro actual.
8. Presionar **Ejecutar prueba solo log** y **Detener ahora** para confirmar que la ejecución segura sigue funcionando.

## Fase 11: edición y reordenamiento de acciones existentes

La Fase 11 actualiza principalmente `app/ui.py` para refinar el constructor manual sin avanzar a ejecución real. La pantalla conserva encabezado, constructor de macros, lista visual de acciones, configuración de macro, macros guardadas, previsualización, log con scroll, ejecución no bloqueante `test_log` y botón **Detener ahora**.

Características principales:

- La lista visual permite seleccionar una acción existente. La acción seleccionada se marca con `▶` y sus datos se cargan en el editor.
- Al seleccionar una acción se restauran sus controles básicos: tecla, modo simple/avanzado cuando corresponde, espera base y variación.
- Botón **Actualizar acción**: toma los valores actuales del editor, valida tecla/delay/variación, reemplaza la acción seleccionada, actualiza la lista visual, prepara la previsualización y registra el cambio en el log.
- Botón **Limpiar selección**: quita la selección actual, deja los controles listos para agregar una acción nueva y no borra acciones existentes.
- Botones **Subir acción** y **Bajar acción**: reordenan la acción seleccionada, mantienen seleccionada la acción movida, actualizan la lista y registran el cambio en el log. Si la acción ya está al inicio o al final, no falla y solo informa que el orden no cambió.
- Botón **Duplicar acción**: duplica la acción seleccionada, inserta la copia después de la original, selecciona la copia y registra el cambio en el log.
- **Agregar acción**, **Eliminar acción** y **Limpiar acciones** siguen funcionando con el mismo enfoque seguro de fases anteriores.
- **Guardar macro** guarda la macro editada con el orden actual de acciones.
- **Cargar macro** e **Importar JSON** llenan acciones, configuración, lista visual, controles básicos y previsualización. Al cargar desde la UI se mantiene `execution_mode = "test_log"`.
- **Exportar JSON** sigue funcionando con macros guardadas o con la macro actual validada.
- **Previsualizar** y **Ejecutar prueba solo log** usan la macro editada actual, incluyendo acciones actualizadas y reordenadas.

Límites de seguridad de Fase 11:

- La ejecución sigue siendo únicamente `test_log`.
- No hay ejecución real de teclas.
- No se puede seleccionar ni ejecutar modo `real`.
- No se puede seleccionar ni ejecutar modo `test_keys`.
- No se implementa grabación de macros, captura de teclado para construir acciones, mouse, clicks, movimientos, `recorder.py`, `player.py`, `duration.py`, `storage.py`, `validation.py` ni estructura `src/`.

### Pruebas rápidas de Fase 11 en PowerShell

Compilar módulos de la aplicación:

```powershell
python -m compileall app
```

Validar una macro `test_log` con dos acciones en el orden actual:

```powershell
python -c "from app.validators import validate_macro_data; data={'app':'Sistema de Macros de V','version':'1.0','actions':[{'key':'enter','base_delay':1.0,'variation_mode':'fixed'},{'key':'space','base_delay':2.0,'variation_mode':'medium'}],'initial_delay':0.0,'repetitions':1,'infinite':False,'cooldown_base':0.0,'cooldown_variation':'fixed','execution_mode':'test_log','key_selection_mode':'simple'}; print(validate_macro_data(data))"
```

Previsualizar una macro `test_log` con dos acciones y confirmar nombres visibles:

```powershell
python -c "from app.preview import build_macro_preview; data={'app':'Sistema de Macros de V','version':'1.0','actions':[{'key':'enter','base_delay':1.0,'variation_mode':'fixed'},{'key':'space','base_delay':2.0,'variation_mode':'medium'}],'initial_delay':0.0,'repetitions':1,'infinite':False,'cooldown_base':0.0,'cooldown_variation':'fixed','execution_mode':'test_log','key_selection_mode':'simple'}; preview=build_macro_preview(data); print(preview['actions_count']); print(preview['actions'][0]['key_display_name']); print(preview['actions'][1]['key_display_name'])"
```

Abrir la UI de Fase 11:

```powershell
python main.py
```

Flujo manual recomendado en la UI:

1. Agregar dos o más acciones desde el constructor.
2. Seleccionar una acción en la lista y confirmar que sus datos aparecen en el editor.
3. Cambiar tecla, espera o variación y presionar **Actualizar acción**.
4. Usar **Subir acción** y **Bajar acción** para comprobar que el orden visual cambia y se conserva la selección.
5. Usar **Limpiar selección** y confirmar que las acciones existentes no se borran.
6. Guardar, cargar, importar o exportar una macro y confirmar que se respeta el orden actual.
7. Presionar **Previsualizar** y **Ejecutar prueba solo log** para confirmar que usan las acciones actualizadas/reordenadas.
8. Usar **Detener ahora** durante una prueba para confirmar que la parada segura sigue operativa.

## Pendiente para Fase 12

Para una fase posterior quedan pendientes, si se aprueban explícitamente, previsualización modal más completa u otros refinamientos visuales. La ejecución real de teclas y `test_keys` deben seguir bloqueados hasta que exista una fase autorizada con controles de seguridad completos.
