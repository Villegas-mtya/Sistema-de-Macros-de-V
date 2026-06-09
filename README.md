# Sistema de Macros de V

Sistema de Macros de V será una aplicación de escritorio en Python para construir macros manuales de teclado.

## Alcance de esta fase

Esta segunda fase prepara rutas seguras para datos de usuario y compatibilidad de rutas para ejecución como script `.py` o como `.exe` empaquetado con PyInstaller.

En esta fase todavía no se implementa ejecución de macros. Por seguridad, la ejecución real de teclas no será flujo recomendado hasta que existan y funcionen F9 global y el botón **Detener ahora**.

## Lo que esta aplicación no hace

- No graba macros automáticamente.
- No captura mouse.
- No ejecuta clicks.
- No mueve el mouse.
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
