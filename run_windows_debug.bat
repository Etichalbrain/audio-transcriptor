@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo AudioTranscriptor - debug run
echo ============================================
echo.

if exist "dist\AudioTranscriptor.exe" (
  echo Avvio: dist\AudioTranscriptor.exe
  echo.
  "dist\AudioTranscriptor.exe"
  echo.
  echo Codice uscita: %ERRORLEVEL%
  pause
  exit /b %ERRORLEVEL%
)

if exist "AudioTranscriptor.exe" (
  echo Avvio: AudioTranscriptor.exe
  echo.
  "AudioTranscriptor.exe"
  echo.
  echo Codice uscita: %ERRORLEVEL%
  pause
  exit /b %ERRORLEVEL%
)

echo EXE non trovato.
echo Metti questo file nella cartella del progetto oppure nella stessa cartella dell'EXE.
echo.
pause
exit /b 1
