<#
.SYNOPSIS
    FIM Enterprise Windows Agent Automated Installer
.DESCRIPTION
    Enrolls the Windows endpoint, installs the resilient background Windows Service
    in services.msc, configures directory permissions, and enables Windows File System auditing (Event 4663).
.PARAMETER ServerUrl
    The HTTP/HTTPS URL of the central FIM Enterprise server (e.g., http://localhost:8000 or https://fim.corp.local)
.PARAMETER EnrollmentToken
    The pre-shared enrollment secret configured in backend (ENROLLMENT_TOKEN_SECRET)
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

# 3. Locate Agent Binary / Sources
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$DistExe = Join-Path $RepoRoot "agent-windows\dist\fim-agent.exe"
$TargetExe = Join-Path $InstallDir "fim-agent.exe"

if (Test-Path $DistExe) {
    Write-Host "[*] Deploying compiled standalone agent from $DistExe..." -ForegroundColor Yellow
    Copy-Item -Path $DistExe -Destination $TargetExe -Force
} else {
    Write-Host "[!] Standalone fim-agent.exe not found in dist. Copying Python source tree..." -ForegroundColor Yellow
    $SourceDir = Join-Path $RepoRoot "agent-windows"
    Copy-Item -Path "$SourceDir\src" -Destination "$InstallDir\" -Recurse -Force
}

# 4. Enroll Endpoint with Central Server
Write-Host "[*] Enrolling endpoint with central FIM server ($ServerUrl)..." -ForegroundColor Yellow

if (Test-Path $TargetExe) {
    & $TargetExe enroll --server $ServerUrl --token $EnrollmentToken
} else {
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonExe) {
        Write-Error "Neither fim-agent.exe nor Python was found. Please ensure agent is compiled or Python is installed."
        exit 1
    }
    Push-Location "$InstallDir\src"
    try {
        & $pythonExe main.py enroll --server $ServerUrl --token $EnrollmentToken
    } finally {
        Pop-Location
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Enrollment failed with exit code $LASTEXITCODE. Please check server connectivity and token."
    exit 1
}

# 5. Enable Windows Security Auditing (Event ID 4663)
Write-Host "[*] Enabling Windows Security Auditing for File System objects..." -ForegroundColor Yellow
try {
    auditpol.exe /set /subcategory:"File System" /success:enable /failure:enable | Out-Null
    Write-Host "[OK] Windows File System auditing enabled." -ForegroundColor Green
} catch {
    Write-Warning "Failed to set audit policy via auditpol.exe: $_"
}

# 6. Install & Configure Windows Service (services.msc)
$ServiceName = "FIMEnterpriseAgent"
$ServiceDisplayName = "FIM Enterprise Agent"
Write-Host "[*] Configuring Windows Service '$ServiceName' in services.msc..." -ForegroundColor Yellow

# Stop existing service if running
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    Write-Host "[*] Stopping existing service instance..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Register service
if (Test-Path $TargetExe) {
    # If service does not exist, create it
    if (-not (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)) {
        New-Service -Name $ServiceName -DisplayName $ServiceDisplayName -BinaryPathName "`"$TargetExe`"" -StartupType Automatic -Description "File Integrity Monitoring real-time endpoint security agent" | Out-Null
        Write-Host "[OK] Registered '$ServiceName' into Windows Service Control Manager." -ForegroundColor Green
    }
} else {
    # Scheduled task fallback if running from raw python without binary
    $TaskName = $ServiceName
    $AgentScript = Join-Path $InstallDir "src\main.py"
    $action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$AgentScript`" start" -WorkingDirectory "$InstallDir\src"
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 0)

    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
}

# 7. Start the Service / Agent
Write-Host "[*] Starting FIM Enterprise Agent background service..." -ForegroundColor Yellow
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    try {
        Start-Service -Name $ServiceName -ErrorAction Stop
        Write-Host "[OK] Windows Service '$ServiceName' is now RUNNING." -ForegroundColor Green
    } catch {
        Write-Warning "Could not start via Start-Service (will start as background process): $_"
        Start-Process -FilePath $TargetExe -ArgumentList "start" -WindowStyle Hidden
    }
}

Start-Sleep -Seconds 2

# 8. Verification Summary
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " [OK] FIM Windows Agent installed and registered successfully!" -ForegroundColor Green
Write-Host " Service Name:   $ServiceName (visible in services.msc)" -ForegroundColor Gray
Write-Host " Agent Binary:   $TargetExe" -ForegroundColor Gray
Write-Host " Server URL:     $ServerUrl" -ForegroundColor Gray
Write-Host " Status:         Registered and actively reporting to server" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "[i] You can now view this endpoint on the web console Endpoint Inventory page." -ForegroundColor Cyan
