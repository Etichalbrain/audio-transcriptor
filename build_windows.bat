@echo off
setlocal

cd /d "%~dp0"

echo ============================================
echo AudioTranscriptor - Windows EXE builder
echo ============================================
echo.
echo Cartella progetto:
echo %CD%
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
  echo Installa Python da https://www.python.org/downloads/windows/
  echo Durante l'installazione seleziona "Add Python to PATH".
  goto error
)

echo Uso Python:
%PYTHON_CMD% --version
if errorlevel 1 goto error

if not exist .venv (
  echo Creo ambiente Python locale...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto error
)

if not exist ".venv\Scripts\activate.bat" (
  echo Ambiente Python non valido: manca .venv\Scripts\activate.bat
  echo Cancella la cartella .venv e rilancia questo file.
  goto error
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto error

echo.
echo Installo strumenti di build...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto error

echo.
echo Installo dipendenze app...
python -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo Installo PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 goto error

echo.
echo Creo il file EXE...
pyinstaller --noconfirm AudioTranscriptor.spec
if errorlevel 1 goto error

echo.
echo ============================================
echo Build completata.
echo File da aprire/condividere:
echo dist\AudioTranscriptor.exe
echo ============================================
echo.
pause
exit /b 0

:error
echo.
echo ============================================
echo ERRORE: la build non e' stata completata.
echo Copia il testo di questa finestra o fai uno screenshot.
echo ============================================
echo.
pause
exit /b 1
