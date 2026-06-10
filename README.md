# Sistema de Macros de V

Sistema de Macros de V será una aplicación de escritorio en Python para construir macros manuales de teclado.

## Alcance actual

El proyecto ya integra las Fases 1 a 6 sobre una base segura y progresiva:

- **Fase 4**: almacenamiento, carga, listado, borrado, importación y exportación de macros en JSON.
- **Fase 5**: previsualización declarativa y estimación de duración antes de ejecutar.
- **Fase 6**: runner de simulación en modo prueba **solo log**.

La aplicación ya puede reconocer teclas en modo simple y avanzado, convertirlas a valores internos estables, validar macros guardables, previsualizar duración y recorrer una macro validada sin presionar teclas reales.

Por seguridad, la ejecución real de teclas todavía no está implementada. Los modos `real` y `test_keys` se rechazan en el runner de Fase 6 hasta que existan controles de emergencia como F9 global y el botón operativo **Detener ahora**.

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

La Fase 3 solo validaba y normalizaba teclas; la Fase 4 agrega almacenamiento JSON; la Fase 5 agrega previsualización; y la Fase 6 agrega un runner seguro que simula la ejecución únicamente con eventos de log.

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

## Build inicial

```bat
build.bat
```

El build inicial usa PyInstaller en modo `--onedir` y no falla si `assets/app_icon.ico` no existe.

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
- `list_saved_macros()`: devuelve una lista ordenada de rutas `Path` a macros `.json` internas.
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

F9 global, listener global, ejecución real de teclas, botón operativo **Detener ahora** e integración visual con `app/ui.py` quedan para fases posteriores. Esta fase permite probar el flujo de ejecución sin riesgo porque todo queda limitado a logs.

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
- La Fase 7 no implementa todavía botón visual **Detener ahora**, integración con `app/ui.py`, modal gráfico, ejecución real, `test_keys`, mouse, clicks ni grabación de macros.

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
