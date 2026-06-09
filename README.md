# Sistema de Macros de V

Sistema de Macros de V será una aplicación de escritorio en Python para construir macros manuales de teclado.

## Alcance de esta fase

Esta tercera fase completa el mapeo, normalización y validación de teclas para macros manuales de teclado. La aplicación ya puede reconocer teclas en modo simple y modo avanzado, y convertirlas a valores internos estables para JSON.

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
- No guarda macros funcionales todavía.
- No importa macros funcionales todavía.

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

Esta fase solo valida y normaliza teclas; no guarda, importa ni ejecuta macros todavía.

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
