$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& '.\.venv\Scripts\python.exe' -m pip install 'pyinstaller==6.22.3'
if ($LASTEXITCODE -ne 0) { throw 'Installation de PyInstaller impossible.' }
& '.\.venv\Scripts\python.exe' -m PyInstaller --noconfirm packaging\methode.spec
if ($LASTEXITCODE -ne 0) { throw 'Construction de l executable impossible.' }
Write-Host 'Executable disponible : dist\CyAICodex\CyAICodex.exe'
Write-Host 'Conservez le dossier _internal avec l executable. Utilisez l installateur pour les mises a jour.'
