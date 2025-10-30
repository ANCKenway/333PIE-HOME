# ================================================================
# 333HOME Agent - Installation Rapide Windows (PowerShell)
# ================================================================
# Usage: Clic droit > "Exécuter avec PowerShell" OU en admin
# ================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  333HOME Agent - Installation Rapide" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$INSTALL_DIR = "$env:ProgramFiles\333HOME Agent"
$HUB_URL = "ws://100.115.207.11:8000/api/ws/agents"
$AGENT_ID = $env:COMPUTERNAME
$PACKAGE_URL = "http://100.115.207.11:8000/static/agents/agent_latest.zip"

# ================================================================
# Vérification Admin
# ================================================================

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[!] Ce script nécessite les droits administrateur" -ForegroundColor Yellow
    Write-Host "[!] Relancez PowerShell en tant qu'administrateur" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

Write-Host "[✓] Droits administrateur confirmés" -ForegroundColor Green
Write-Host ""

# ================================================================
# Vérification Python
# ================================================================

Write-Host "[+] Vérification Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python installé : $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Python non trouvé dans le PATH" -ForegroundColor Red
    Write-Host "    Téléchargez Python 3.11+ depuis https://python.org" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}
Write-Host ""

# ================================================================
# Arrêt agent existant
# ================================================================

Write-Host "[+] Arrêt des agents existants..." -ForegroundColor Cyan
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[✓] Processus Python arrêtés" -ForegroundColor Green
Write-Host ""

# ================================================================
# Nettoyage installation précédente
# ================================================================

if (Test-Path $INSTALL_DIR) {
    Write-Host "[+] Nettoyage installation précédente..." -ForegroundColor Cyan
    Remove-Item "$INSTALL_DIR\*" -Recurse -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Write-Host "[✓] Nettoyage terminé" -ForegroundColor Green
} else {
    Write-Host "[+] Création du dossier d'installation..." -ForegroundColor Cyan
    New-Item -Path $INSTALL_DIR -ItemType Directory -Force | Out-Null
    Write-Host "[✓] Dossier créé : $INSTALL_DIR" -ForegroundColor Green
}
Write-Host ""

# ================================================================
# Téléchargement package
# ================================================================

Write-Host "[+] Téléchargement du package agent..." -ForegroundColor Cyan
$TEMP_ZIP = "$env:TEMP\333home_agent.zip"

try {
    Invoke-WebRequest -Uri $PACKAGE_URL -OutFile $TEMP_ZIP -UseBasicParsing
    $fileSize = (Get-Item $TEMP_ZIP).Length
    Write-Host "[✓] Package téléchargé ($fileSize bytes)" -ForegroundColor Green
} catch {
    Write-Host "[✗] Échec du téléchargement" -ForegroundColor Red
    Write-Host "    URL: $PACKAGE_URL" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}
Write-Host ""

# ================================================================
# Extraction package (gestion auto sous-dossier)
# ================================================================

Write-Host "[+] Extraction des fichiers..." -ForegroundColor Cyan

# Extraire dans temp
$TEMP_EXTRACT = "$env:TEMP\333home_extract"
if (Test-Path $TEMP_EXTRACT) {
    Remove-Item $TEMP_EXTRACT -Recurse -Force
}
Expand-Archive -Path $TEMP_ZIP -DestinationPath $TEMP_EXTRACT -Force

# Vérifier structure (sous-dossier ou fichiers à plat)
$extractedItems = Get-ChildItem $TEMP_EXTRACT
if ($extractedItems.Count -eq 1 -and $extractedItems[0].PSIsContainer) {
    # Structure avec sous-dossier agent_vX.X.X
    Write-Host "    Structure ZIP: sous-dossier détecté" -ForegroundColor Gray
    $sourceDir = $extractedItems[0].FullName
} else {
    # Structure à plat
    Write-Host "    Structure ZIP: fichiers à plat" -ForegroundColor Gray
    $sourceDir = $TEMP_EXTRACT
}

# Copier fichiers vers install dir
Copy-Item -Path "$sourceDir\*" -Destination $INSTALL_DIR -Recurse -Force

# Nettoyer
Remove-Item $TEMP_ZIP -Force
Remove-Item $TEMP_EXTRACT -Recurse -Force

Write-Host "[✓] Fichiers extraits dans $INSTALL_DIR" -ForegroundColor Green
Write-Host ""

# ================================================================
# Installation dépendances
# ================================================================

Write-Host "[+] Installation des dépendances Python..." -ForegroundColor Cyan
Write-Host "    (cela peut prendre 1-2 minutes)" -ForegroundColor Gray
Write-Host ""

Set-Location $INSTALL_DIR

# Installer dépendances
python -m pip install --quiet --upgrade pip
python -m pip install --quiet websockets pydantic psutil aiohttp pystray Pillow

if ($LASTEXITCODE -ne 0) {
    Write-Host "[✗] Échec installation dépendances" -ForegroundColor Red
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

Write-Host "[✓] Dépendances installées" -ForegroundColor Green
Write-Host ""

# ================================================================
# Configuration
# ================================================================

Write-Host "[+] Création de la configuration..." -ForegroundColor Cyan

$config = @{
    agent_id = $AGENT_ID
    hub_url = $HUB_URL
} | ConvertTo-Json

Set-Content -Path "$INSTALL_DIR\tray_config.json" -Value $config -Encoding UTF8

Write-Host "[✓] Configuration créée" -ForegroundColor Green
Write-Host "    Agent ID: $AGENT_ID" -ForegroundColor Gray
Write-Host "    Hub URL: $HUB_URL" -ForegroundColor Gray
Write-Host ""

# ================================================================
# Tâche planifiée
# ================================================================

Write-Host "[+] Création de la tâche planifiée..." -ForegroundColor Cyan

# Supprimer tâche existante
Unregister-ScheduledTask -TaskName "333HOME Agent" -Confirm:$false -ErrorAction SilentlyContinue

# Obtenir pythonw.exe
$pythonPath = (Get-Command python).Source
$pythonwPath = $pythonPath -replace "python.exe", "pythonw.exe"

# Créer action
$action = New-ScheduledTaskAction -Execute $pythonwPath -Argument "`"$INSTALL_DIR\agent_tray.pyw`"" -WorkingDirectory $INSTALL_DIR

# Trigger au login
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Paramètres
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Enregistrer tâche
Register-ScheduledTask -TaskName "333HOME Agent" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null

Write-Host "[✓] Tâche planifiée créée" -ForegroundColor Green
Write-Host "    L'agent démarrera automatiquement au login" -ForegroundColor Gray
Write-Host ""

# ================================================================
# Démarrage agent
# ================================================================

Write-Host "[+] Démarrage de l'agent..." -ForegroundColor Cyan

Start-Process -FilePath $pythonwPath -ArgumentList "`"$INSTALL_DIR\agent_tray.pyw`"" -WindowStyle Hidden

Start-Sleep -Seconds 3

# Vérifier processus
$agentProcess = Get-Process pythonw -ErrorAction SilentlyContinue
if ($agentProcess) {
    Write-Host "[✓] Agent démarré avec succès (PID: $($agentProcess.Id))" -ForegroundColor Green
    Write-Host ""
    Write-Host "    Recherchez l'icône 'H' dans la barre des tâches" -ForegroundColor Cyan
    Write-Host "    (près de l'horloge, coin bas-droit)" -ForegroundColor Cyan
} else {
    Write-Host "[!] L'agent n'a pas démarré" -ForegroundColor Yellow
    Write-Host "    Vérifiez les logs: $INSTALL_DIR\logs\" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Installation Terminée!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Agent ID      : $AGENT_ID" -ForegroundColor White
Write-Host "  Hub URL       : $HUB_URL" -ForegroundColor White
Write-Host "  Installation  : $INSTALL_DIR" -ForegroundColor White
Write-Host ""
Write-Host "  Actions possibles:" -ForegroundColor White
Write-Host "   - Clic droit sur l'icône 'H' pour le menu" -ForegroundColor Gray
Write-Host "   - Logs: $INSTALL_DIR\logs\agent_stdout.log" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Appuyez sur Entrée pour fermer"
