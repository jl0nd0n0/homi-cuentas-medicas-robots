@echo off
setlocal

:: Rutas
set SCRIPT_DIR=C:\tools\robot\homi\wrapper-automation
set BAT_SCRIPT=%SCRIPT_DIR%\run.bat
set TASK_NAME=HOMI_robots_factura_diaria_20_minutos

:: Verificar que existan los archivos
if not exist "%BAT_SCRIPT%" (
    echo ERROR: No se encuentra el archivo %BAT_SCRIPT%
    pause
    exit /b 1
)

:: Eliminar tarea si ya existe
schtasks /Query | findstr /C:"%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% == 0 schtasks /Delete /TN "%TASK_NAME%" /F

:: Crear nueva tarea programada
schtasks /Create /TN "%TASK_NAME%" ^
         /TR "%BAT_SCRIPT%" ^
         /SC MINUTE /MO 20 ^
         /ST 00:00 ^
         /RL HIGHEST ^
         /F

echo.
echo Tarea programada creada: "%TASK_NAME%"
echo Se ejecutara cada 20 minutos.
echo.
echo Puedes verla en: Programador de tareas -> Tareas activadas por tiempo
echo.
pause