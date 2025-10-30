# ================================================================
# 333HOME Agent - Setup Automatique Windows
# ================================================================
# Installation complète de l'agent en tant que service Windows
# 
# Usage:
#   .\setup.ps1
#   .\setup.ps1 -HubUrl "ws://100.115.207.11:8000/api/agents/ws/agents"
#   .\setup.ps1 -AgentId "TITO" -HubUrl "ws://..." -SkipNssm
# ================================================================

<#
.SYNOPSIS
    Installation automatique de l'agent 333HOME comme service Windows

.DESCRIPTION
    Ce script installe l'agent 333HOME en tant que service Windows permanent.
    - Vérifie les prérequis (Python, droits admin)
    - Télécharge NSSM (Non-Sucking Service Manager)
    - Télécharge le package agent depuis le Hub
    - Configure le service avec restart automatique
    - Démarre le service et valide la connexion

.PARAMETER AgentId
    ID unique de l'agent (ex: TITO, LAPTOP01). Par défaut: hostname

.PARAMETER HubUrl
    URL WebSocket du Hub (ex: ws://100.115.207.11:8000/api/agents/ws/agents)

.PARAMETER InstallPath
    Chemin d'installation (par défaut: C:\Program Files\333HOME Agent)

.PARAMETER SkipNssm
    Ne pas télécharger NSSM (déjà présent)

.PARAMETER ServiceName
    Nom du service Windows (par défaut: 333HOME-Agent)

.EXAMPLE
    .\setup.ps1
    Installation avec paramètres par défaut

.EXAMPLE
    .\setup.ps1 -AgentId "TITO" -HubUrl "ws://100.115.207.11:8000/api/agents/ws/agents"
    Installation avec configuration personnalisée
#>

[CmdletBinding()]
param(
    [string]$AgentId = $env:COMPUTERNAME,
    [string]$HubUrl = "ws://100.115.207.11:8000/api/agents/ws/agents",
    [string]$InstallPath = "C:\Program Files\333HOME Agent",
    [switch]$SkipNssm,
    [string]$ServiceName = "333HOME-Agent"
)

# Configuration
$ErrorActionPreference = "Stop"
$PackageUrl = "http://100.115.207.11:8000/static/agents/agent_latest.zip"
$NssmScript = Join-Path $PSScriptRoot "download_nssm.ps1"
$ToolsDir = Join-Path $PSScriptRoot "tools"

# ================================================================
# Fonctions
# ================================================================

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Text)
    Write-Host "[+] $Text" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "[ERROR] $Text" -ForegroundColor Red
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        return $pythonVersion -match "Python 3\.\d+"
    } catch {
        return $false
    }
}

# ================================================================
# Script Principal
# ================================================================

Write-Header "333HOME Agent - Installation Windows Service"

# Étape 1: Vérifier droits administrateur
Write-Step "Checking administrator privileges..."
if (-not (Test-Administrator)) {
    Write-Error "This script requires administrator privileges"
    Write-Host "Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
    exit 1
}
Write-Success "Running as administrator"

# Étape 2: Vérifier Python
Write-Step "Checking Python installation..."
if (-not (Test-PythonInstalled)) {
    Write-Error "Python 3.x not found"
    Write-Host "Please install Python 3.11 or higher from python.org" -ForegroundColor Yellow
    exit 1
}
$pythonVersion = python --version
Write-Success "Python installed: $pythonVersion"

# Obtenir chemin Python
$pythonPath = (Get-Command python).Source
Write-Host "    Python path: $pythonPath" -ForegroundColor Gray

# Étape 3: Télécharger NSSM si nécessaire
if (-not $SkipNssm) {
    Write-Step "Downloading NSSM (service manager)..."
    if (-not (Test-Path $NssmScript)) {
        Write-Error "NSSM download script not found: $NssmScript"
        exit 1
    }
    
    & $NssmScript -TargetDir $ToolsDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to download NSSM"
        exit 1
    }
}

$nssmPath = Join-Path $ToolsDir "nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Error "NSSM.exe not found: $nssmPath"
    exit 1
}
Write-Success "NSSM available: $nssmPath"

# Étape 4: Créer dossier installation
Write-Step "Creating installation directory..."
if (Test-Path $InstallPath) {
    Write-Host "    Directory already exists, will overwrite files" -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}
Write-Success "Installation path: $InstallPath"

# Étape 5: Télécharger package agent
Write-Step "Downloading agent package..."
$packageZip = Join-Path $env:TEMP "333home_agent.zip"

try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $PackageUrl -OutFile $packageZip -UseBasicParsing
    $fileSize = (Get-Item $packageZip).Length / 1KB
    Write-Success "Downloaded: $([math]::Round($fileSize, 2)) KB"
} catch {
    Write-Error "Failed to download agent package: $($_.Exception.Message)"
    Write-Host "    URL: $PackageUrl" -ForegroundColor Gray
    exit 1
}

# Étape 6: Extraire package
Write-Step "Extracting agent files..."
try {
    Expand-Archive -Path $packageZip -DestinationPath $InstallPath -Force
    Write-Success "Files extracted to $InstallPath"
    
    # Nettoyer ZIP
    Remove-Item -Force $packageZip
} catch {
    Write-Error "Failed to extract package: $($_.Exception.Message)"
    exit 1
}

# Vérifier fichier agent.py
$agentScript = Join-Path $InstallPath "agent.py"
if (-not (Test-Path $agentScript)) {
    Write-Error "agent.py not found in package"
    exit 1
}

# Étape 7: Installer dépendances Python
Write-Step "Installing Python dependencies..."
$requirementsFile = Join-Path $InstallPath "requirements.txt"
if (Test-Path $requirementsFile) {
    try {
        python -m pip install --quiet --upgrade pip
        python -m pip install --quiet -r $requirementsFile
        Write-Success "Dependencies installed"
    } catch {
        Write-Error "Failed to install dependencies: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Host "    No requirements.txt found, skipping" -ForegroundColor Yellow
}

# Étape 8: Créer fichier de configuration
Write-Step "Creating configuration file..."
$configFile = Join-Path $InstallPath "agent_config.txt"
@"
AGENT_ID=$AgentId
HUB_URL=$HubUrl
"@ | Out-File -FilePath $configFile -Encoding UTF8
Write-Success "Config saved: $configFile"

# Étape 9: Vérifier si service existe déjà
Write-Step "Checking existing service..."
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "    Service already exists, stopping..." -ForegroundColor Yellow
    
    # Arrêter service
    & $nssmPath stop $ServiceName | Out-Null
    Start-Sleep -Seconds 2
    
    # Désinstaller ancien service
    & $nssmPath remove $ServiceName confirm | Out-Null
    Start-Sleep -Seconds 1
    
    Write-Success "Old service removed"
}

# Étape 10: Installer service NSSM
Write-Step "Installing Windows service..."

# Construire commande agent
$agentArgs = "--agent-id `"$AgentId`" --hub-url `"$HubUrl`" --log-level INFO"

try {
    # Installer service
    & $nssmPath install $ServiceName $pythonPath $agentScript $agentArgs | Out-Null
    
    # Configurer description
    & $nssmPath set $ServiceName Description "333HOME Remote Control Agent - Automated management and monitoring" | Out-Null
    
    # Configurer dossier de travail
    & $nssmPath set $ServiceName AppDirectory $InstallPath | Out-Null
    
    # Configurer restart automatique
    & $nssmPath set $ServiceName AppExit Default Restart | Out-Null
    & $nssmPath set $ServiceName AppRestartDelay 5000 | Out-Null  # 5 secondes
    
    # Configurer logs
    $logDir = Join-Path $InstallPath "logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir | Out-Null
    }
    
    $stdoutLog = Join-Path $logDir "agent_stdout.log"
    $stderrLog = Join-Path $logDir "agent_stderr.log"
    
    & $nssmPath set $ServiceName AppStdout $stdoutLog | Out-Null
    & $nssmPath set $ServiceName AppStderr $stderrLog | Out-Null
    & $nssmPath set $ServiceName AppRotateFiles 1 | Out-Null
    & $nssmPath set $ServiceName AppRotateBytes 10485760 | Out-Null  # 10 MB
    
    # Démarrage automatique
    & $nssmPath set $ServiceName Start SERVICE_AUTO_START | Out-Null
    
    Write-Success "Service installed: $ServiceName"
    
} catch {
    Write-Error "Failed to install service: $($_.Exception.Message)"
    exit 1
}

# Étape 11: Démarrer service
Write-Step "Starting service..."
try {
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 3
    
    # Vérifier statut
    $service = Get-Service -Name $ServiceName
    if ($service.Status -eq "Running") {
        Write-Success "Service started successfully"
    } else {
        throw "Service status: $($service.Status)"
    }
} catch {
    Write-Error "Failed to start service: $($_.Exception.Message)"
    Write-Host "Check logs: $stdoutLog" -ForegroundColor Yellow
    exit 1
}

# Étape 12: Validation finale
Write-Header "Installation Complete"

Write-Success "Agent ID: $AgentId"
Write-Success "Hub URL: $HubUrl"
Write-Success "Install Path: $InstallPath"
Write-Success "Service Name: $ServiceName"
Write-Success "Service Status: Running"

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Verify agent connection in Hub dashboard" -ForegroundColor White
Write-Host "  2. Check logs: $stdoutLog" -ForegroundColor White
Write-Host "  3. Manage service: services.msc" -ForegroundColor White
Write-Host ""
Write-Host "Service management commands:" -ForegroundColor Cyan
Write-Host "  Start:   Start-Service $ServiceName" -ForegroundColor White
Write-Host "  Stop:    Stop-Service $ServiceName" -ForegroundColor White
Write-Host "  Restart: Restart-Service $ServiceName" -ForegroundColor White
Write-Host "  Status:  Get-Service $ServiceName" -ForegroundColor White
Write-Host ""

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Installation Successful!" -ForegroundColor Green
Write-Host "  Agent is now running as a Windows service" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
