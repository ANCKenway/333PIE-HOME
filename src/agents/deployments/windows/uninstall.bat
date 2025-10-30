@echo off
REM ================================================================
REM 333HOME Agent - Désinstallation Windows
REM ================================================================
REM Désinstallation propre avec backup des logs
REM ================================================================

setlocal EnableDelayedExpansion

echo.
echo ================================================================
echo   333HOME Agent - Desinstallation
echo ================================================================
echo.

REM ================================================================
REM Configuration
REM ================================================================

set "INSTALL_DIR=%ProgramFiles%\333HOME Agent"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\333HOME Agent.lnk"
set "BACKUP_DIR=%USERPROFILE%\Documents\333HOME\logs_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%"

REM ================================================================
REM Vérification droits administrateur
REM ================================================================

echo [+] Verification des droits administrateur...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERREUR] Ce script necessite les droits administrateur
    echo.
    echo Faites un clic droit sur uninstall.bat et selectionnez
    echo "Executer en tant qu'administrateur"
    echo.
    pause
    exit /b 1
)
echo [OK] Droits administrateur confirmes
echo.

REM ================================================================
REM Confirmation
REM ================================================================

echo ATTENTION: Cette action va completement desinstaller l'agent 333HOME
echo.
echo  - Arret de l'agent
echo  - Suppression de la tache planifiee
echo  - Backup des logs
echo  - Suppression du dossier d'installation
echo  - Suppression du raccourci Bureau
echo.

set /p CONFIRM="Voulez-vous continuer? (oui/non) : "
if /I not "%CONFIRM%"=="oui" (
    echo.
    echo Desinstallation annulee
    echo.
    pause
    exit /b 0
)

echo.

REM ================================================================
REM Arrêt agent
REM ================================================================

echo [+] Arret de l'agent...

REM Tuer tous les processus pythonw.exe liés à l'agent
for /f "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq pythonw.exe" /FO TABLE /NH 2^>nul ^| find /I "pythonw.exe"') do (
    echo     Arret processus PID %%p...
    taskkill /PID %%p /F >nul 2>&1
)

REM Attendre 2 secondes
timeout /t 2 >nul

echo [OK] Agent arrete
echo.

REM ================================================================
REM Suppression tâche planifiée
REM ================================================================

echo [+] Suppression de la tache planifiee...

schtasks /Query /TN "333HOME Agent" >nul 2>&1
if %errorLevel% equ 0 (
    schtasks /Delete /TN "333HOME Agent" /F >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] Tache planifiee supprimee
    ) else (
        echo [ERREUR] Echec suppression tache planifiee
    )
) else (
    echo [OK] Aucune tache planifiee trouvee
)
echo.

REM ================================================================
REM Backup logs
REM ================================================================

echo [+] Backup des logs...

if exist "%INSTALL_DIR%\logs" (
    if not exist "%BACKUP_DIR%" (
        mkdir "%BACKUP_DIR%" 2>nul
    )
    
    xcopy "%INSTALL_DIR%\logs\*.*" "%BACKUP_DIR%\" /E /I /Q >nul 2>&1
    
    if %errorLevel% equ 0 (
        echo [OK] Logs sauvegardes dans:
        echo     %BACKUP_DIR%
    ) else (
        echo [ERREUR] Echec backup logs
    )
) else (
    echo [OK] Aucun log a sauvegarder
)
echo.

REM ================================================================
REM Suppression dossier installation
REM ================================================================

echo [+] Suppression du dossier d'installation...

if exist "%INSTALL_DIR%" (
    REM Supprimer attributs read-only récursivement
    attrib -r "%INSTALL_DIR%\*.*" /s >nul 2>&1
    
    REM Supprimer dossier
    rd /s /q "%INSTALL_DIR%" 2>nul
    
    if not exist "%INSTALL_DIR%" (
        echo [OK] Dossier supprime: %INSTALL_DIR%
    ) else (
        echo [ERREUR] Echec suppression dossier
        echo Vous devrez peut-etre le supprimer manuellement
    )
) else (
    echo [OK] Dossier d'installation deja supprime
)
echo.

REM ================================================================
REM Suppression raccourci Bureau
REM ================================================================

echo [+] Suppression du raccourci Bureau...

if exist "%SHORTCUT%" (
    del "%SHORTCUT%" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] Raccourci supprime
    ) else (
        echo [ERREUR] Echec suppression raccourci
    )
) else (
    echo [OK] Aucun raccourci trouve
)
echo.

REM ================================================================
REM Vérification finale
REM ================================================================

echo [+] Verification finale...

set ERRORS=0

REM Vérifier processus
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "agent_tray" >nul 2>&1
if %errorLevel% equ 0 (
    echo [ERREUR] Processus agent encore actif
    set /a ERRORS+=1
)

REM Vérifier dossier
if exist "%INSTALL_DIR%" (
    echo [ERREUR] Dossier installation encore present
    set /a ERRORS+=1
)

REM Vérifier tâche
schtasks /Query /TN "333HOME Agent" >nul 2>&1
if %errorLevel% equ 0 (
    echo [ERREUR] Tache planifiee encore presente
    set /a ERRORS+=1
)

if %ERRORS% equ 0 (
    echo [OK] Verification completee - Aucun probleme detecte
) else (
    echo [ERREUR] %ERRORS% probleme(s) detecte(s)
    echo Verifiez manuellement et supprimez si necessaire
)
echo.

REM ================================================================
REM Désinstallation terminée
REM ================================================================

echo.
echo ================================================================
if %ERRORS% equ 0 (
    echo   Desinstallation Terminee avec Succes!
) else (
    echo   Desinstallation Terminee avec Avertissements
)
echo ================================================================
echo.

if exist "%BACKUP_DIR%" (
    echo  Logs sauvegardes dans:
    echo    %BACKUP_DIR%
    echo.
)

echo  Pour reinstaller l'agent:
echo    Executez install.bat
echo.
echo ================================================================
echo.

pause
