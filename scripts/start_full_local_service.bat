@echo off
setlocal

set "WORKFLOW_ROOT=%~dp0.."
set "GPT_SOVITS_ROOT=%~1"
if "%GPT_SOVITS_ROOT%"=="" set "GPT_SOVITS_ROOT=%CD%"

set "YUKI_INNER_API_PORT=9884"
set "YUKI_ROUTER_PORT=9883"
set "YUKI_CONFIG=GPT_SoVITS\configs\tts_infer_yuki_v4.yaml"

if not exist "%GPT_SOVITS_ROOT%\runtime\python.exe" (
  echo Usage:
  echo   scripts\start_full_local_service.bat C:\path\to\GPT-SoVITS
  echo.
  echo Could not find runtime\python.exe under:
  echo   %GPT_SOVITS_ROOT%
  exit /b 1
)
if not exist "%GPT_SOVITS_ROOT%\%YUKI_CONFIG%" (
  echo Missing config:
  echo   %GPT_SOVITS_ROOT%\%YUKI_CONFIG%
  exit /b 1
)

set "PATH=%GPT_SOVITS_ROOT%\runtime;%PATH%"
set "PYTHONIOENCODING=utf-8"
set "HF_HOME=%GPT_SOVITS_ROOT%\TEMP\hf_home"
set "TRANSFORMERS_CACHE=%GPT_SOVITS_ROOT%\TEMP\hf_cache"
set "HF_HUB_CACHE=%GPT_SOVITS_ROOT%\TEMP\hf_hub"

echo Starting GPT-SoVITS raw API on http://127.0.0.1:%YUKI_INNER_API_PORT%/docs
start "Yuki GPT-SoVITS raw API :%YUKI_INNER_API_PORT%" /D "%GPT_SOVITS_ROOT%" cmd /k "runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p %YUKI_INNER_API_PORT% -c %YUKI_CONFIG%"

echo Waiting before starting the local TTS router...
timeout /t 8 /nobreak >nul

echo Starting local TTS router on http://127.0.0.1:%YUKI_ROUTER_PORT%/docs
"%GPT_SOVITS_ROOT%\runtime\python.exe" "%WORKFLOW_ROOT%\scripts\local_tts_router.py" ^
  --refs "%WORKFLOW_ROOT%\refs\emotion_refs.json" ^
  --gpt-sovits-api "http://127.0.0.1:%YUKI_INNER_API_PORT%" ^
  --host 0.0.0.0 ^
  --port %YUKI_ROUTER_PORT%

echo.
echo Local TTS router exited with code %ERRORLEVEL%.
pause
