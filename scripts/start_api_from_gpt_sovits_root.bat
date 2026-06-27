@echo off
setlocal
cd /d "%~dp0\.."

set "YUKI_API_PORT=9883"
set "YUKI_CONFIG=GPT_SoVITS\configs\tts_infer_yuki_v4.yaml"

if not exist "runtime\python.exe" (
  echo Run this script from a GPT-SoVITS root, or copy it into that root before running.
  exit /b 1
)
if not exist "%YUKI_CONFIG%" (
  echo Missing config: %YUKI_CONFIG%
  exit /b 1
)

set "PATH=%CD%\runtime;%PATH%"
set "PYTHONIOENCODING=utf-8"
set "HF_HOME=%CD%\TEMP\hf_home"
set "TRANSFORMERS_CACHE=%CD%\TEMP\hf_cache"
set "HF_HUB_CACHE=%CD%\TEMP\hf_hub"

set "PORT_PID="
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%YUKI_API_PORT% .*LISTENING"') do set "PORT_PID=%%P"
if defined PORT_PID (
  echo Port %YUKI_API_PORT% is already in use by PID %PORT_PID%.
  tasklist /FI "PID eq %PORT_PID%"
  exit /b 1
)

echo Starting Yuki GPT-SoVITS v4 API on http://127.0.0.1:%YUKI_API_PORT%/docs
runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p %YUKI_API_PORT% -c %YUKI_CONFIG%
echo.
echo API exited with code %ERRORLEVEL%.
pause
