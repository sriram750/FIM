<#
.SYNOPSIS
    Builds Windows MSI Installer for FIM Enterprise Agent
.DESCRIPTION
    Generates a standard Windows Installer package (.msi) using WiX Toolset
    or packages the self-installing executable bundle.
#>

$SourceExe = Join-Path $PSScriptRoot "..\dist\fim-agent.exe"
$OutputDir = Join-Path $PSScriptRoot "..\dist"
$MsiOutput = Join-Path $OutputDir "fim-agent-installer.msi"

if (-not (Test-Path $SourceExe)) {
    Write-Host "[*] Compiling fim-agent.exe first..." -ForegroundColor Yellow
    & ".\.venv\Scripts\python.exe" (Join-Path $PSScriptRoot "build_exe.py")
}

Write-Host "[*] Packaging MSI installer for FIM Enterprise Windows Agent..." -ForegroundColor Cyan

$PythonExe = Join-Path $PSScriptRoot "..\..\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python.exe"
}

$BuildScript = Join-Path $PSScriptRoot "build_msi.py"
Write-Host "[*] Executing MSI generator: $BuildScript..." -ForegroundColor Cyan
& $PythonExe $BuildScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Windows agent MSI installer package created successfully." -ForegroundColor Green
} else {
    Write-Host "[!] MSI build failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
