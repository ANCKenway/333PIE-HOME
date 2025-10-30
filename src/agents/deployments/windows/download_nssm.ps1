# ================================================================
# 333HOME Agent - NSSM Downloader
# ================================================================
# Télécharge NSSM (Non-Sucking Service Manager) depuis GitHub
# NSSM permet de transformer n'importe quel programme en service Windows
# ================================================================

<#
.SYNOPSIS
    Télécharge et installe NSSM pour Windows

.DESCRIPTION
    Script pour télécharger automatiquement NSSM depuis le site officiel.
    NSSM est utilisé pour transformer l'agent Python en service Windows.

.EXAMPLE
    .\download_nssm.ps1
#>

param(
    [string]$TargetDir = ".\tools",
    [string]$NssmVersion = "2.24"
)

# Configuration
$ErrorActionPreference = "Stop"
$NssmUrl = "https://nssm.cc/release/nssm-$NssmVersion.zip"
$TempZip = "$env:TEMP\nssm.zip"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  333HOME Agent - NSSM Download" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Créer dossier tools si nécessaire
if (-not (Test-Path $TargetDir)) {
    Write-Host "[+] Creating tools directory: $TargetDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

# Vérifier si NSSM déjà présent
$NssmExe = Join-Path $TargetDir "nssm.exe"
if (Test-Path $NssmExe) {
    Write-Host "[OK] NSSM already exists: $NssmExe" -ForegroundColor Green
    
    # Afficher version
    $version = & $NssmExe --version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Version: $version" -ForegroundColor Green
    Write-Host ""
    exit 0
}

# Télécharger NSSM
Write-Host "[+] Downloading NSSM $NssmVersion..." -ForegroundColor Yellow
Write-Host "    URL: $NssmUrl" -ForegroundColor Gray

try {
    $ProgressPreference = 'SilentlyContinue'  # Masquer barre progression
    Invoke-WebRequest -Uri $NssmUrl -OutFile $TempZip -UseBasicParsing
    Write-Host "[OK] Download completed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to download NSSM: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Vérifier taille fichier
$fileSize = (Get-Item $TempZip).Length / 1KB
Write-Host "[OK] File size: $([math]::Round($fileSize, 2)) KB" -ForegroundColor Green

# Extraire NSSM
Write-Host "[+] Extracting NSSM..." -ForegroundColor Yellow

try {
    # Créer dossier temporaire pour extraction
    $tempExtract = Join-Path $env:TEMP "nssm_extract"
    if (Test-Path $tempExtract) {
        Remove-Item -Recurse -Force $tempExtract
    }
    New-Item -ItemType Directory -Path $tempExtract | Out-Null
    
    # Extraire archive
    Expand-Archive -Path $TempZip -DestinationPath $tempExtract -Force
    
    # Détecter architecture système
    $arch = if ([Environment]::Is64BitOperatingSystem) { "win64" } else { "win32" }
    Write-Host "[OK] Detected architecture: $arch" -ForegroundColor Green
    
    # Copier NSSM.exe vers dossier tools
    $nssmSource = Get-ChildItem -Path $tempExtract -Filter "nssm.exe" -Recurse | 
                  Where-Object { $_.FullName -like "*\$arch\*" } | 
                  Select-Object -First 1
    
    if ($nssmSource) {
        Copy-Item -Path $nssmSource.FullName -Destination $NssmExe -Force
        Write-Host "[OK] NSSM extracted to: $NssmExe" -ForegroundColor Green
    } else {
        throw "NSSM.exe not found in archive"
    }
    
    # Nettoyer fichiers temporaires
    Remove-Item -Recurse -Force $tempExtract
    Remove-Item -Force $TempZip
    
} catch {
    Write-Host "[ERROR] Failed to extract NSSM: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Vérifier installation
if (Test-Path $NssmExe) {
    Write-Host ""
    Write-Host "[SUCCESS] NSSM installed successfully!" -ForegroundColor Green
    
    # Afficher version
    $version = & $NssmExe --version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Version: $version" -ForegroundColor Green
    Write-Host "[OK] Path: $NssmExe" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[ERROR] Installation failed - NSSM.exe not found" -ForegroundColor Red
    exit 1
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  NSSM Ready!" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
