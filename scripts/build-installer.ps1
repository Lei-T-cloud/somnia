$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$app = Get-ChildItem "release" -Directory | Where-Object { $_.Name -ne "build" } | Select-Object -First 1
if (-not $app) {
    throw "Missing desktop app folder. Run scripts/build-exe.ps1 first."
}

$iscc = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $iscc) {
    throw "Inno Setup 6 is not installed."
}

& $iscc "desktop\somnia.iss"
if ($LASTEXITCODE -ne 0) {
    throw "Installer compile failed."
}

Write-Host "installer ready in release/"
