# Sistema de Macros de V

Sistema de Macros de V será una aplicación de escritorio en Python para construir macros manuales de teclado.

## Alcance de esta fase

Esta primera fase prepara la estructura obligatoria del proyecto y una ventana inicial mínima con CustomTkinter.

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

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
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
