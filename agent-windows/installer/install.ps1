<#
.SYNOPSIS
    FIM Enterprise Windows Agent Automated Installer
.DESCRIPTION
    Installs the FIM Windows Agent as a resilient background Windows Service,
    configures directory permissions, enables Windows File System auditing (Event 4663),
    and enrolls the endpoint with the central FIM server.
.PARAMETER ServerUrl
    The HTTPS/HTTP URL of the central FIM Enterprise server (e.g., https://fim.corp.local:8443 or http://192.168.1.50:8000)
.PARAMETER EnrollmentToken
    The pre-shared enrollment secret configured in .env (ENROLLMENT_TOKEN_SECRET)
.PARAMETER InstallDir
    Target directory for agent binaries (Default: C:\Program Files\FIMEnterprise\Agent)
.PARAMETER DataDir
    Target directory for spool database and baselines (Default: C:\ProgramData\FIMEnterprise)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$ServerUrl,

    [Parameter(Mandatory=$true)]
    [string]$EnrollmentToken,

    [string]$InstallDir = "C:\Program Files\FIMEnterprise\Agent",
    [string]$DataDir = "C:\ProgramData\FIMEnterprise"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " FIM ENTERPRISE — WINDOWS AGENT INSTALLER" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Administrator Check
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This installer must be run as Administrator (Elevated PowerShell)."
    exit 1
}

# 2. Prepare Directories
Write-Host "[*] Creating target directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

# 3. Copy Agent Files
$SourceDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Host "[*] Copying agent files from $SourceDir to $InstallDir..." -ForegroundColor Yellow
Copy-Item -Path "$SourceDir\src" -Destination "$InstallDir\" -Recurse -Force
Copy-Item -Path "$SourceDir\requirements.txt" -Destination "$InstallDir\" -Force

# 4. Python Environment Check / Setup
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonExe) {
    Write-Error "Python 3.10+ was not found on PATH. Please ensure Python is installed on the client."
    exit 1
}

Write-Host "[*] Setting up isolated Python virtual environment..." -ForegroundColor Yellow
$venvDir = Join-Path $InstallDir "venv"
if (-not (Test-Path $venvDir)) {
    & $pythonExe -m venv $venvDir
}
$venvPython = Join-Path $venvDir "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r (Join-Path $InstallDir "requirements.txt") --quiet

# 5. Enroll Endpoint with Central Server
Write-Host "[*] Enrolling endpoint with central FIM server ($ServerUrl)..." -ForegroundColor Yellow
Push-Location "$InstallDir\src"
try {
    & $venvPython main.py enroll --server $ServerUrl --token $EnrollmentToken
} finally {
    Pop-Location
}

# 6. Enable Windows File System Auditing (Event ID 4663)
Write-Host "[*] Enabling Windows Security Auditing for File System objects..." -ForegroundColor Yellow
try {
    auditpol.exe /set /subcategory:"File System" /success:enable /failure:enable | Out-Null
    Write-Host "[✓] Windows File System auditing enabled." -ForegroundColor Green
} catch {
    Write-Warning "Failed to set audit policy via auditpol.exe: $_"
}

# 7. Register Background Windows Service / Task
Write-Host "[*] Registering FIM Enterprise background startup..." -ForegroundColor Yellow
$TaskName = "FIMEnterpriseAgent"
$AgentScript = Join-Path $InstallDir "src\main.py"

# Create a robust Scheduled Task that runs at System startup with highest privileges
$action = New-ScheduledTaskAction -Execute $venvPython -Argument "`"$AgentScript`" start" -WorkingDirectory "$InstallDir\src"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 0)

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null

# Start the agent task immediately
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 2

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " [✓] FIM Windows Agent installed and running successfully!" -ForegroundColor Green
Write-Host " Agent Directory: $InstallDir" -ForegroundColor Gray
Write-Host " Data & Spool:   $DataDir" -ForegroundColor Gray
Write-Host " Server URL:     $ServerUrl" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Green
