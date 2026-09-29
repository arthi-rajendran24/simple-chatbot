@echo off
setlocal
cd /d "%~dp0"
if "%PORT%"=="" set PORT=8181
if "%CHAT_MODEL%"=="" set CHAT_MODEL=gemma4:e2b

where python >nul 2>&1
if errorlevel 1 (
  echo Python 3.10+ is required. Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  exit /b 1
)
where ollama >nul 2>&1
if errorlevel 1 (
  echo Ollama is required. Install it from https://ollama.com/download and run this again.
  exit /b 1
)

ollama list 2>nul | findstr /i /c:"%CHAT_MODEL%" >nul
if errorlevel 1 (
  echo Downloading model %CHAT_MODEL% - one time only...
  ollama pull %CHAT_MODEL%
  if errorlevel 1 (
    echo Could not pull the model. Make sure Ollama is running, then try again.
    exit /b 1
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo Setting up - first run only...
  python -m venv .venv || exit /b 1
  ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || exit /b 1
)

start "" "http://localhost:%PORT%"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port %PORT%
