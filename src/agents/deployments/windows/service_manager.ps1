# ================================================================
# 333HOME Agent - Service Manager
# ================================================================
# Utilitaire de gestion du service agent Windows
# 
# Usage:
#   .\service_manager.ps1 -Action status
#   .\service_manager.ps1 -Action start
#   .\service_manager.ps1 -Action stop
#   .\service_manager.ps1 -Action restart
#   .\service_manager.ps1 -Action logs
#   .\service_manager.ps1 -Action update
# ================================================================

<#
.SYNOPSIS
    Gestion du service 333HOME Agent

.DESCRIPTION
    Script pour gérer facilement le service agent Windows:
    - start: Démarrer le service
    - stop: Arrêter le service
    - restart: Redémarrer le service
    - status: Afficher le statut détaillé
    - logs: Afficher les logs en temps réel
    - update: Télécharger et installer une nouvelle version

.PARAMETER Action
    Action à effectuer (start, stop, restart, status, logs, update)

.PARAMETER ServiceName
    Nom du service (par défaut: 333HOME-Agent)

.PARAMETER Version
    Version à installer pour l'action 'update' (ex: 1.0.15)

.EXAMPLE
    .\service_manager.ps1 -Action status
    Affiche le statut du service

.EXAMPLE
    .\service_manager.ps1 -Action update -Version 1.0.16
    Met à jour vers la version 1.0.16
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "update")]
    [string]$Action,
    
    [string]$ServiceName = "333HOME-Agent",
    [string]$Version = "latest"
)

# Configuration
$ErrorActionPreference = "Stop"
$InstallPath = "C:\Program Files\333HOME Agent"
$LogsPath = Join-Path $InstallPath "logs"
$StdoutLog = Join-Path $LogsPath "agent_stdout.log"
$StderrLog = Join-Path $LogsPath "agent_stderr.log"

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

function Get-ServiceInfo {
    param([string]$Name)
    
    $service = Get-Service -Name $Name -ErrorAction SilentlyContinue
    if (-not $service) {
        return $null
    }
    
    # Obtenir info détaillée via WMI
    $wmiService = Get-WmiObject -Class Win32_Service -Filter "Name='$Name'"
    
    # Calculer uptime si running
    $uptime = $null
    if ($service.Status -eq "Running") {
        $process = Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*$InstallPath*" } | Select-Object -First 1
        if ($process) {
            $uptime = (Get-Date) - $process.StartTime
        }
    }
    
    return @{
        Service = $service
        WmiService = $wmiService
        Uptime = $uptime
    }
}

function Format-Uptime {
    param([TimeSpan]$Uptime)
    
    if ($null -eq $Uptime) {
        return "N/A"
    }
    
    $days = $Uptime.Days
    $hours = $Uptime.Hours
    $minutes = $Uptime.Minutes
    $seconds = $Uptime.Seconds
    
    $parts = @()
    if ($days -gt 0) { $parts += "$days day(s)" }
    if ($hours -gt 0) { $parts += "$hours hour(s)" }
    if ($minutes -gt 0) { $parts += "$minutes min(s)" }
    if ($seconds -gt 0 -and $days -eq 0) { $parts += "$seconds sec(s)" }
    
    return ($parts -join " ")
}

function Show-Status {
    Write-Header "333HOME Agent - Service Status"
    
    $info = Get-ServiceInfo -Name $ServiceName
    
    if (-not $info) {
        Write-Error "Service not found: $ServiceName"
        Write-Host "Run setup.ps1 to install the agent" -ForegroundColor Yellow
        return
    }
    
    $service = $info.Service
    $wmi = $info.WmiService
    
    # Status principal
    $statusColor = if ($service.Status -eq "Running") { "Green" } else { "Red" }
    Write-Host "Service Name:    " -NoNewline
    Write-Host $service.Name -ForegroundColor White
    Write-Host "Display Name:    " -NoNewline
    Write-Host $service.DisplayName -ForegroundColor White
    Write-Host "Status:          " -NoNewline
    Write-Host $service.Status -ForegroundColor $statusColor
    Write-Host "Start Type:      " -NoNewline
    Write-Host $wmi.StartMode -ForegroundColor White
    
    # Uptime
    if ($info.Uptime) {
        Write-Host "Uptime:          " -NoNewline
        Write-Host (Format-Uptime $info.Uptime) -ForegroundColor Cyan
    }
    
    # Paths
    Write-Host ""
    Write-Host "Install Path:    " -NoNewline
    Write-Host $InstallPath -ForegroundColor Gray
    Write-Host "Stdout Log:      " -NoNewline
    Write-Host $StdoutLog -ForegroundColor Gray
    Write-Host "Stderr Log:      " -NoNewline
    Write-Host $StderrLog -ForegroundColor Gray
    
    # Recent logs
    Write-Host ""
    Write-Host "Recent logs (last 10 lines):" -ForegroundColor Cyan
    if (Test-Path $StdoutLog) {
        Get-Content $StdoutLog -Tail 10 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    } else {
        Write-Host "  No logs found" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

function Start-AgentService {
    Write-Header "Starting 333HOME Agent Service"
    
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if (-not $service) {
        Write-Error "Service not found: $ServiceName"
        return
    }
    
    if ($service.Status -eq "Running") {
        Write-Success "Service is already running"
        return
    }
    
    Write-Step "Starting service..."
    try {
        Start-Service -Name $ServiceName
        Start-Sleep -Seconds 2
        
        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq "Running") {
            Write-Success "Service started successfully"
        } else {
            Write-Error "Service status: $($service.Status)"
        }
    } catch {
        Write-Error "Failed to start service: $($_.Exception.Message)"
    }
}

function Stop-AgentService {
    Write-Header "Stopping 333HOME Agent Service"
    
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if (-not $service) {
        Write-Error "Service not found: $ServiceName"
        return
    }
    
    if ($service.Status -ne "Running") {
        Write-Success "Service is already stopped"
        return
    }
    
    Write-Step "Stopping service..."
    try {
        Stop-Service -Name $ServiceName -Force
        Start-Sleep -Seconds 2
        
        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq "Stopped") {
            Write-Success "Service stopped successfully"
        } else {
            Write-Error "Service status: $($service.Status)"
        }
    } catch {
        Write-Error "Failed to stop service: $($_.Exception.Message)"
    }
}

function Restart-AgentService {
    Write-Header "Restarting 333HOME Agent Service"
    
    Stop-AgentService
    Start-Sleep -Seconds 1
    Start-AgentService
}

function Show-Logs {
    Write-Header "333HOME Agent - Live Logs"
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-Path $StdoutLog)) {
        Write-Error "Log file not found: $StdoutLog"
        return
    }
    
    # Tail -f style
    Get-Content $StdoutLog -Tail 50 -Wait
}

function Update-Agent {
    Write-Header "333HOME Agent - Update Service"
    
    # Vérifier droits admin
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "Update requires administrator privileges"
        return
    }
    
    # URL package
    $packageUrl = if ($Version -eq "latest") {
        "http://100.115.207.11:8000/static/agents/agent_latest.zip"
    } else {
        "http://100.115.207.11:8000/static/agents/agent_v$Version.zip"
    }
    
    Write-Step "Downloading version: $Version"
    Write-Host "    URL: $packageUrl" -ForegroundColor Gray
    
    $packageZip = Join-Path $env:TEMP "333home_agent_update.zip"
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $packageUrl -OutFile $packageZip -UseBasicParsing
        $fileSize = (Get-Item $packageZip).Length / 1KB
        Write-Success "Downloaded: $([math]::Round($fileSize, 2)) KB"
    } catch {
        Write-Error "Failed to download: $($_.Exception.Message)"
        return
    }
    
    # Arrêter service
    Write-Step "Stopping service..."
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Backup version actuelle
    Write-Step "Creating backup..."
    $backupDir = Join-Path $InstallPath ".backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    
    try {
        $filesToBackup = @("agent.py", "config.py", "remote_logging.py", "plugins")
        foreach ($item in $filesToBackup) {
            $source = Join-Path $InstallPath $item
            if (Test-Path $source) {
                $dest = Join-Path $backupDir $item
                if (-not (Test-Path (Split-Path $dest))) {
                    New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
                }
                Copy-Item -Path $source -Destination $dest -Recurse -Force
            }
        }
        Write-Success "Backup created: $backupDir"
    } catch {
        Write-Error "Failed to create backup: $($_.Exception.Message)"
    }
    
    # Extraire nouvelle version
    Write-Step "Extracting new version..."
    try {
        Expand-Archive -Path $packageZip -DestinationPath $InstallPath -Force
        Write-Success "Files updated"
        Remove-Item -Force $packageZip
    } catch {
        Write-Error "Failed to extract: $($_.Exception.Message)"
        return
    }
    
    # Redémarrer service
    Write-Step "Starting service..."
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 2
    
    $service = Get-Service -Name $ServiceName
    if ($service.Status -eq "Running") {
        Write-Success "Update completed successfully"
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "  Agent Updated to Version $Version" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Error "Service failed to start after update"
        Write-Host "Check logs: $StdoutLog" -ForegroundColor Yellow
    }
}

# ================================================================
# Exécution Action
# ================================================================

switch ($Action) {
    "status"  { Show-Status }
    "start"   { Start-AgentService }
    "stop"    { Stop-AgentService }
    "restart" { Restart-AgentService }
    "logs"    { Show-Logs }
    "update"  { Update-Agent }
}
