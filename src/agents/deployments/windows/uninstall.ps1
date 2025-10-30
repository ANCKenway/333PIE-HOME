# ================================================================
# 333HOME Agent - Désinstallation Windows
# ================================================================
# Désinstalle proprement le service agent Windows
# 
# Usage:
#   .\uninstall.ps1
#   .\uninstall.ps1 -KeepLogs
#   .\uninstall.ps1 -ServiceName "333HOME-Agent"
# ================================================================

<#
.SYNOPSIS
    Désinstalle l'agent 333HOME de Windows

.DESCRIPTION
    Ce script désinstalle complètement le service agent Windows:
    - Arrête le service
    - Désinstalle le service NSSM
    - Sauvegarde les logs
    - Supprime les fichiers d'installation
    - Nettoie le système

.PARAMETER ServiceName
    Nom du service à désinstaller (par défaut: 333HOME-Agent)

.PARAMETER InstallPath
    Chemin d'installation (par défaut: C:\Program Files\333HOME Agent)

.PARAMETER KeepLogs
    Conserver les logs dans Documents\333HOME\logs

.PARAMETER Force
    Ne pas demander de confirmation

.EXAMPLE
    .\uninstall.ps1
    Désinstallation avec confirmation

.EXAMPLE
    .\uninstall.ps1 -Force -KeepLogs
    Désinstallation sans confirmation, logs conservés
#>

[CmdletBinding()]
param(
    [string]$ServiceName = "333HOME-Agent",
    [string]$InstallPath = "C:\Program Files\333HOME Agent",
    [switch]$KeepLogs,
    [switch]$Force
)

# Configuration
$ErrorActionPreference = "Stop"
$ToolsDir = Join-Path $PSScriptRoot "tools"
$NssmPath = Join-Path $ToolsDir "nssm.exe"

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

# ================================================================
# Script Principal
# ================================================================

Write-Header "333HOME Agent - Uninstallation"

# Vérifier droits administrateur
Write-Step "Checking administrator privileges..."
if (-not (Test-Administrator)) {
    Write-Error "This script requires administrator privileges"
    Write-Host "Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
    exit 1
}
Write-Success "Running as administrator"

# Confirmation
if (-not $Force) {
    Write-Host ""
    Write-Host "WARNING: This will completely remove the 333HOME Agent service" -ForegroundColor Yellow
    Write-Host "  Service: $ServiceName" -ForegroundColor White
    Write-Host "  Path: $InstallPath" -ForegroundColor White
    Write-Host ""
    $confirmation = Read-Host "Are you sure you want to continue? (yes/no)"
    
    if ($confirmation -ne "yes") {
        Write-Host "Uninstallation cancelled" -ForegroundColor Yellow
        exit 0
    }
}

# Étape 1: Vérifier service existe
Write-Step "Checking service..."
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if (-not $service) {
    Write-Host "    Service not found: $ServiceName" -ForegroundColor Yellow
} else {
    Write-Success "Service found: $ServiceName (Status: $($service.Status))"
    
    # Étape 2: Arrêter service
    if ($service.Status -eq "Running") {
        Write-Step "Stopping service..."
        try {
            Stop-Service -Name $ServiceName -Force
            Start-Sleep -Seconds 2
            Write-Success "Service stopped"
        } catch {
            Write-Error "Failed to stop service: $($_.Exception.Message)"
        }
    }
    
    # Étape 3: Désinstaller service
    Write-Step "Uninstalling service..."
    if (Test-Path $NssmPath) {
        try {
            & $NssmPath remove $ServiceName confirm | Out-Null
            Start-Sleep -Seconds 1
            Write-Success "Service uninstalled"
        } catch {
            Write-Error "Failed to uninstall service: $($_.Exception.Message)"
        }
    } else {
        Write-Host "    NSSM not found, trying sc.exe..." -ForegroundColor Yellow
        try {
            sc.exe delete $ServiceName | Out-Null
            Write-Success "Service removed via sc.exe"
        } catch {
            Write-Error "Failed to remove service"
        }
    }
}

# Étape 4: Sauvegarder logs si demandé
if ($KeepLogs) {
    Write-Step "Backing up logs..."
    $logSource = Join-Path $InstallPath "logs"
    $logBackup = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "333HOME\logs_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    
    if (Test-Path $logSource) {
        try {
            if (-not (Test-Path (Split-Path $logBackup))) {
                New-Item -ItemType Directory -Path (Split-Path $logBackup) -Force | Out-Null
            }
            Copy-Item -Path $logSource -Destination $logBackup -Recurse -Force
            Write-Success "Logs backed up to: $logBackup"
        } catch {
            Write-Error "Failed to backup logs: $($_.Exception.Message)"
        }
    } else {
        Write-Host "    No logs found to backup" -ForegroundColor Yellow
    }
}

# Étape 5: Supprimer dossier installation
Write-Step "Removing installation directory..."
if (Test-Path $InstallPath) {
    try {
        Remove-Item -Path $InstallPath -Recurse -Force
        Write-Success "Installation directory removed"
    } catch {
        Write-Error "Failed to remove directory: $($_.Exception.Message)"
        Write-Host "    You may need to remove it manually: $InstallPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "    Installation directory not found" -ForegroundColor Yellow
}

# Étape 6: Validation finale
Write-Step "Verifying uninstallation..."
$serviceCheck = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
$dirCheck = Test-Path $InstallPath

if (-not $serviceCheck -and -not $dirCheck) {
    Write-Header "Uninstallation Complete"
    Write-Success "Service removed successfully"
    Write-Success "Installation directory cleaned"
    
    if ($KeepLogs) {
        Write-Host ""
        Write-Host "Logs backup location: $logBackup" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  333HOME Agent Successfully Uninstalled" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Uninstallation completed with warnings:" -ForegroundColor Yellow
    if ($serviceCheck) {
        Write-Host "  - Service still exists: $ServiceName" -ForegroundColor Yellow
    }
    if ($dirCheck) {
        Write-Host "  - Directory still exists: $InstallPath" -ForegroundColor Yellow
    }
    Write-Host "Please check manually and remove if necessary" -ForegroundColor Yellow
    Write-Host ""
}
