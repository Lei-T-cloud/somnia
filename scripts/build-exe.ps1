$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "1/4 安装前端依赖并打包"
npm install
npm run build

Write-Host "2/4 安装桌面打包依赖"
$py = "backend\.venv\Scripts\python.exe"
& $py -m pip install -r backend\requirements.txt -r desktop\requirements.txt

Write-Host "3/4 生成 Windows exe"
& $py -m PyInstaller desktop\somnia.spec --noconfirm --distpath release --workpath release\build

Write-Host "4/4 完成"
Write-Host "可执行文件：release\眠栖Somnia\眠栖Somnia.exe"
