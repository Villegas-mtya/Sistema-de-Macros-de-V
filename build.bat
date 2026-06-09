@echo off
setlocal

REM Build inicial de Sistema de Macros de V.
REM La aplicación funciona aunque assets\app_icon.ico todavía no exista.

python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

set ICON_ARG=
if exist assets\app_icon.ico set ICON_ARG=--icon assets\app_icon.ico

pyinstaller --onedir --windowed --name "Sistema de Macros de V" %ICON_ARG% main.py
endlocal
