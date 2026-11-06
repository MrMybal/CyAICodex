$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& npm ci --prefix .CyDocBuild
if ($LASTEXITCODE -ne 0) { throw 'Documentation dependencies installation failed.' }
& npm --prefix .CyDocBuild run build
if ($LASTEXITCODE -ne 0) { throw 'Documentation generation failed.' }
& '.\.venv\Scripts\python.exe' -m pip install 'pyinstaller==6.22.3'
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller installation failed.' }
& '.\.venv\Scripts\python.exe' -m PyInstaller --noconfirm packaging\cyaicodex.spec
if ($LASTEXITCODE -ne 0) { throw 'Application build failed.' }
Write-Host 'Application available: dist\CyAICodex\CyAICodex.exe'
Write-Host 'Keep _internal and Documentation next to the executable. Use the installer for updates.'
