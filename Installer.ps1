$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 ou plus recent est requis.' }
}
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Installation des dependances impossible.' }
Write-Host 'Installation terminee. Double-cliquez sur Demarrer.vbs.'
