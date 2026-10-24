@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo AudioTranscriptor - Windows installer builder
echo ============================================
echo.
echo Cartella progetto:
echo %CD%
echo.

set PYTHON_CMD=
where py >nul 2>nul
if not errorlevel 1 set PYTHON_CMD=py -3.12
if "%PYTHON_CMD%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set PYTHON_CMD=python
)

if "%PYTHON_CMD%"=="" (
  echo Python non trovato.
  echo Installa Python 3.12 da https://www.python.org/downloads/windows/
  echo Durante l'installazione seleziona "Add Python to PATH".
  goto error
)

echo Uso Python:
%PYTHON_CMD% --version
if errorlevel 1 (
  echo Python 3.12 non disponibile, provo il comando "python".
  set PYTHON_CMD=python
  python --version
  if errorlevel 1 goto error
)

if not exist ".venv\Scripts\python.exe" (
  echo Creo ambiente Python locale...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto error
)

echo.
echo Installo dipendenze...
".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto error

echo.
echo Creo la cartella applicazione...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean AudioTranscriptorWindows.spec
if errorlevel 1 goto error

if not exist "dist\AudioTranscriptor\AudioTranscriptor.exe" (
  echo Build incompleta: manca dist\AudioTranscriptor\AudioTranscriptor.exe
  goto error
)

rem I documenti legali viaggiano con l'app, dentro il setup e nello zip portable.
copy /Y LICENSE "dist\AudioTranscriptor\LICENSE.txt" >nul
copy /Y LICENSE-SUPPLEMENT.md "dist\AudioTranscriptor\LICENSE-SUPPLEMENT.md" >nul
copy /Y NOTICE "dist\AudioTranscriptor\NOTICE" >nul
copy /Y PRIVACY.md "dist\AudioTranscriptor\PRIVACY.md" >nul
copy /Y TERMS.md "dist\AudioTranscriptor\TERMS.md" >nul
copy /Y THIRD_PARTY_NOTICES.md "dist\AudioTranscriptor\THIRD_PARTY_NOTICES.md" >nul
copy /Y installer\LEGGIMI.txt "dist\AudioTranscriptor\LEGGIMI.txt" >nul
if exist licenses xcopy /E /I /Y licenses "dist\AudioTranscriptor\licenses" >nul
if not exist "dist\AudioTranscriptor\LICENSE.txt" (
  echo Build incompleta: manca LICENSE.txt nella cartella dell'app
  goto error
)
if not exist "dist\AudioTranscriptor\THIRD_PARTY_NOTICES.md" (
  echo Build incompleta: mancano le note di terze parti nella cartella dell'app
  goto error
)

echo.
echo Cerco Inno Setup 6...
set ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" set ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" (
  echo Inno Setup 6 non trovato.
  echo Scaricalo da https://jrsoftware.org/isdl.php e reinstalla questo file.
  goto error
)

echo.
echo Creo il setup di installazione...
"%ISCC%" "installer\audio_transcriptor.iss"
if errorlevel 1 goto error

echo.
echo ============================================
echo Build completata.
echo Installer: installer\Output\AudioTranscriptorSetup-1.0.1.exe
echo Cartella portable: dist\AudioTranscriptor\
echo ============================================
echo.
echo In alternativa puoi far compilare tutto a GitHub Actions:
echo   gh workflow run build-windows.yml
echo.
pause
exit /b 0

:error
echo.
echo ============================================
echo ERRORE: build non completata.
echo Copia il testo di questa finestra per diagnosticare.
echo ============================================
echo.
pause
exit /b 1
