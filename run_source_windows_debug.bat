@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo AudioTranscriptor - source debug
echo ============================================
echo.

if not exist ".venv\Scripts\activate.bat" (
  echo Virtualenv non trovata. Prima esegui build_windows.bat.
  pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m audio_transcriptor
echo.
echo Codice uscita: %ERRORLEVEL%
pause
