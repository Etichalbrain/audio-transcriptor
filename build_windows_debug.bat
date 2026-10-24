@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo AudioTranscriptor - DEBUG EXE builder
echo ============================================
echo.

set PYTHON_CMD=
where py >nul 2>nul
if not errorlevel 1 (
  set PYTHON_CMD=py -3
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set PYTHON_CMD=python
  )
)

if "%PYTHON_CMD%"=="" (
  echo Python non trovato.
  echo Installa Python e seleziona "Add Python to PATH".
  goto error
)

if not exist .venv (
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto error
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto error

python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto error

python -m pip install -r requirements.txt
if errorlevel 1 goto error

python -m pip install pyinstaller
if errorlevel 1 goto error

echo.
echo Creo EXE debug con console...
pyinstaller --noconfirm AudioTranscriptorDebug.spec
if errorlevel 1 goto error

echo.
echo ============================================
echo Build debug completata.
echo Apri questo file:
echo dist\AudioTranscriptor Debug.exe
echo.
echo Se si chiude o mostra errore, copia qui il testo.
echo ============================================
pause
exit /b 0

:error
echo.
echo ERRORE nella build debug.
pause
exit /b 1
