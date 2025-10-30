@echo off
REM ================================================================
REM 333HOME Agent - Installation Automatique Windows
REM ================================================================
REM Installation simple en 1 double-clic avec icon tray
REM ================================================================

setlocal EnableDelayedExpansion

echo.
echo ================================================================
echo   333HOME Agent - Installation Automatique
echo ================================================================
echo.

REM ================================================================
REM Configuration
REM ================================================================

set "INSTALL_DIR=%ProgramFiles%\333HOME Agent"
set "HUB_URL=ws://100.115.207.11:8000/api/agents/ws/agents"
set "AGENT_ID=%COMPUTERNAME%"
set "PACKAGE_URL=http://100.115.207.11:8000/static/agents/agent_latest.zip"

REM ================================================================
REM Vérification droits administrateur
REM ================================================================

echo [+] Verification des droits administrateur...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERREUR] Ce script necessite les droits administrateur
    echo.
    echo Faites un clic droit sur install.bat et selectionnez
    echo "Executer en tant qu'administrateur"
    echo.
    pause
    exit /b 1
)
echo [OK] Droits administrateur confirmes
echo.

REM ================================================================
REM Vérification Python
REM ================================================================

echo [+] Verification installation Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo.
    echo Telechargez Python 3.11+ depuis https://python.org
    echo N'oubliez pas de cocher "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo [OK] Python installe : %PYTHON_VERSION%
echo.

REM ================================================================
REM Création dossier installation
REM ================================================================

echo [+] Creation du dossier d'installation...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo [OK] Dossier cree : %INSTALL_DIR%
) else (
    echo [OK] Dossier existant : %INSTALL_DIR%
)
echo.

REM ================================================================
REM Téléchargement package agent
REM ================================================================

echo [+] Telechargement du package agent...
set "TEMP_ZIP=%TEMP%\333home_agent.zip"

REM PowerShell pour télécharger
powershell -Command "& {Invoke-WebRequest -Uri '%PACKAGE_URL%' -OutFile '%TEMP_ZIP%' -UseBasicParsing}" 2>nul
if %errorLevel% neq 0 (
    echo [ERREUR] Echec du telechargement
    echo Verifiez la connexion au Hub : %PACKAGE_URL%
    echo.
    pause
    exit /b 1
)

REM Vérifier taille fichier
for %%A in ("%TEMP_ZIP%") do set SIZE=%%~zA
if %SIZE% lss 1000 (
    echo [ERREUR] Fichier telecharge trop petit (possiblement erreur 404)
    del "%TEMP_ZIP%"
    pause
    exit /b 1
)

echo [OK] Package telecharge (%SIZE% bytes)
echo.

REM ================================================================
REM Extraction package
REM ================================================================

echo [+] Extraction des fichiers...
powershell -Command "& {Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%INSTALL_DIR%' -Force}" 2>nul
if %errorLevel% neq 0 (
    echo [ERREUR] Echec de l'extraction
    pause
    exit /b 1
)

REM Nettoyer ZIP
del "%TEMP_ZIP%"

echo [OK] Fichiers extraits dans %INSTALL_DIR%
echo.

REM ================================================================
REM Installation dépendances Python
REM ================================================================

echo [+] Installation des dependances Python...
echo     (cela peut prendre 1-2 minutes)
echo.

cd /d "%INSTALL_DIR%"

REM Installer pip si nécessaire
python -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [+] Installation de pip...
    python -m ensurepip --default-pip
)

REM Installer dépendances
python -m pip install --quiet --upgrade pip
python -m pip install --quiet websockets pydantic psutil aiohttp pystray Pillow

if %errorLevel% neq 0 (
    echo [ERREUR] Echec installation dependances
    echo.
    pause
    exit /b 1
)

echo [OK] Dependances installees
echo.

REM ================================================================
REM Création configuration
REM ================================================================

echo [+] Creation de la configuration...

REM Créer fichier config JSON pour tray
echo { > "%INSTALL_DIR%\tray_config.json"
echo   "agent_id": "%AGENT_ID%", >> "%INSTALL_DIR%\tray_config.json"
echo   "hub_url": "%HUB_URL%" >> "%INSTALL_DIR%\tray_config.json"
echo } >> "%INSTALL_DIR%\tray_config.json"

echo [OK] Configuration creee
echo     Agent ID: %AGENT_ID%
echo     Hub URL: %HUB_URL%
echo.

REM ================================================================
REM Création tâche planifiée
REM ================================================================

echo [+] Creation de la tache planifiee Windows...

REM Supprimer tâche existante si présente
schtasks /Query /TN "333HOME Agent" >nul 2>&1
if %errorLevel% equ 0 (
    schtasks /Delete /TN "333HOME Agent" /F >nul 2>&1
)

REM Obtenir chemin pythonw.exe (sans console)
for /f "tokens=*" %%p in ('where python') do set PYTHON_PATH=%%p
set PYTHONW_PATH=!PYTHON_PATH:python.exe=pythonw.exe!

REM Créer tâche qui démarre au login + boot
schtasks /Create /TN "333HOME Agent" /TR "\"%PYTHONW_PATH%\" \"%INSTALL_DIR%\agent_tray.pyw\"" /SC ONLOGON /RL HIGHEST /F >nul 2>&1

if %errorLevel% neq 0 (
    echo [ERREUR] Echec creation tache planifiee
    echo L'agent devra etre lance manuellement
) else (
    echo [OK] Tache planifiee creee
    echo     L'agent demarrera automatiquement au login
)
echo.

REM ================================================================
REM Création raccourci Bureau
REM ================================================================

echo [+] Creation du raccourci Bureau...

set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\333HOME Agent.lnk"

REM PowerShell pour créer raccourci
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%PYTHONW_PATH%'; $Shortcut.Arguments = '\"%INSTALL_DIR%\agent_tray.pyw\"'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = '333HOME Remote Agent'; $Shortcut.Save()"

if %errorLevel% equ 0 (
    echo [OK] Raccourci cree sur le Bureau
) else (
    echo [ERREUR] Echec creation raccourci
)
echo.

REM ================================================================
REM Démarrage agent
REM ================================================================

echo [+] Demarrage de l'agent...

REM Lancer agent_tray.pyw avec pythonw (pas de console)
start "" "%PYTHONW_PATH%" "%INSTALL_DIR%\agent_tray.pyw"

timeout /t 3 >nul

REM Vérifier processus lancé
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "pythonw.exe" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Agent demarre avec succes
    echo.
    echo     Recherchez l'icone "H" dans la barre des taches
    echo     (pres de l'horloge, coins bas-droite)
    echo.
) else (
    echo [ERREUR] L'agent n'a pas demarre
    echo Lancez manuellement: %DESKTOP%\333HOME Agent.lnk
    echo.
)

REM ================================================================
REM Installation terminée
REM ================================================================

echo.
echo ================================================================
echo   Installation Terminee avec Succes!
echo ================================================================
echo.
echo  Agent ID      : %AGENT_ID%
echo  Hub URL       : %HUB_URL%
echo  Installation  : %INSTALL_DIR%
echo.
echo  Actions possibles:
echo   - Clic droit sur l'icone "H" dans la barre des taches
echo   - Raccourci Bureau: 333HOME Agent.lnk
echo   - Logs: %INSTALL_DIR%\logs\agent_stdout.log
echo.
echo  L'agent demarrera automatiquement au prochain login Windows
echo.
echo ================================================================
echo.

pause
