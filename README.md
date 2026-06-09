# Sistema de Macros de V

Sistema de Macros de V será una aplicación de escritorio en Python para construir macros manuales de teclado.

## Alcance de esta fase

Esta cuarta fase agrega almacenamiento, carga, importación y exportación de macros en JSON sobre la base de mapeo, normalización y validación de teclas de Fase 3. La aplicación ya puede reconocer teclas en modo simple y modo avanzado, convertirlas a valores internos estables y validar la estructura básica de una macro guardable.

En esta fase todavía no se implementa ejecución de macros. Por seguridad, la ejecución real de teclas no será flujo recomendado hasta que existan y funcionen F9 global y el botón **Detener ahora**.

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

La Fase 3 solo validaba y normalizaba teclas; la Fase 4 agrega almacenamiento JSON, pero todavía no ejecuta macros.

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

La Fase 4 agrega almacenamiento, carga, importación y exportación de macros en archivos `.json`. Esta fase solo trabaja con datos: todavía no ejecuta macros, no activa F9 global, no implementa un runner operativo, no captura teclado para grabar acciones y no agrega mouse, clicks ni movimientos.

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
