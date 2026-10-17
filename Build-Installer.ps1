param([string]$Iscc = '')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& "$PSScriptRoot\Build-App.ps1"
if (-not $Iscc) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    $Iscc = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $Iscc -or -not (Test-Path -LiteralPath $Iscc)) { throw 'Install Inno Setup 6 or pass the ISCC.exe path with -Iscc.' }
& $Iscc 'packaging\CyAICodex.iss'
if ($LASTEXITCODE -ne 0) { throw 'Installer build failed.' }
Write-Host 'Installer available in dist.'
