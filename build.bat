@echo off
setlocal EnableExtensions

REM Build seguro con PyInstaller para Sistema de Macros de V.
REM Fase 22 habilita ejecucion real controlada solo con seleccion explicita y confirmacion.
REM test_log sigue como modo seguro por defecto; test_keys sigue bloqueado.

pushd "%~dp0"

set "APP_NAME=Sistema de Macros de V"
set "EXE_PATH=dist\%APP_NAME%\%APP_NAME%.exe"
set "ICON_ARG="

if not exist "main.py" (
    echo [ERROR] No se encontro main.py. Ejecuta build.bat desde la raiz del proyecto.
    popd
    exit /b 1
)

if not exist "requirements.txt" (
    echo [ERROR] No se encontro requirements.txt. No se pueden instalar dependencias.
    popd
    exit /b 1
)

if not exist "assets" (
    echo [ERROR] No se encontro la carpeta assets requerida para --add-data.
    popd
    exit /b 1
)

if not exist "examples" (
    echo [ERROR] No se encontro la carpeta examples requerida para --add-data.
    popd
    exit /b 1
)

echo [INFO] Instalando/actualizando dependencias desde requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias.
    popd
    exit /b 1
)

echo [INFO] Verificando PyInstaller...
python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller no esta disponible. Instala dependencias con: python -m pip install -r requirements.txt
    popd
    exit /b 1
)

if exist "assets\app_icon.ico" (
    echo [INFO] Icono detectado: assets\app_icon.ico
    set "ICON_ARG=--icon=assets\app_icon.ico"
) else (
    echo [INFO] No existe assets\app_icon.ico; se construira sin icono personalizado.
)

echo [INFO] Limpiando builds previos...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [INFO] Generando ejecutable seguro en modo ventana...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --windowed ^
    --name "%APP_NAME%" ^
    --add-data "assets;assets" ^
    --add-data "examples;examples" ^
    --collect-data customtkinter ^
    %ICON_ARG% ^
    main.py

if errorlevel 1 (
    echo [ERROR] PyInstaller no pudo generar el ejecutable.
    popd
    exit /b 1
)

if exist "%EXE_PATH%" (
    echo [OK] Ejecutable generado: %EXE_PATH%
) else (
    echo [WARN] PyInstaller termino, pero no se encontro el ejecutable esperado: %EXE_PATH%
    echo [WARN] Revisa la carpeta dist para confirmar la salida generada.
)

echo [INFO] Fase 22 habilita ejecucion real controlada solo con seleccion explicita y confirmacion.
echo [INFO] test_log sigue como modo seguro por defecto; test_keys sigue bloqueado.
popd
endlocal
