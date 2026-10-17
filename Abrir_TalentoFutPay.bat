@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creando el entorno local de TalentoFutPay...
    python -m venv .venv
    if errorlevel 1 (
        echo No se pudo crear el entorno. Instala Python 3 y vuelve a intentarlo.
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
    if errorlevel 1 (
        echo No se pudieron instalar las dependencias de requirements.txt.
        pause
        exit /b 1
    )
)

start "TalentoFutPay - Navegador" /min cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000/"

".venv\Scripts\python.exe" app.py

pause
