@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No se encontro el entorno virtual de la aplicacion.
    echo Verifica que este archivo este dentro de E:\TALENTOFUTPAY.
    pause
    exit /b 1
)

start "TalentoFutPay - Navegador" /min cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000/"

.venv\Scripts\python.exe app.py

pause
