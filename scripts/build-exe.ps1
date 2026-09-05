$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "1/4 frontend"
npm install
npm run build

Write-Host "2/4 desktop deps"
$py = "backend\.venv\Scripts\python.exe"
& $py -m pip install -r backend\requirements.txt -r desktop\requirements.txt

Write-Host "3/4 pyinstaller"
& $py -m PyInstaller desktop\somnia.spec --noconfirm --distpath release --workpath release\build

Write-Host "4/5 installer"
powershell -ExecutionPolicy Bypass -File .\scripts\build-installer.ps1

Write-Host "5/5 done"
