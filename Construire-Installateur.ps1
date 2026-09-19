param([string]$Iscc = '')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& "$PSScriptRoot\Construire-Exe.ps1"
if (-not $Iscc) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    $Iscc = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $Iscc -or -not (Test-Path -LiteralPath $Iscc)) { throw 'Installez Inno Setup 6 ou fournissez -Iscc avec le chemin de ISCC.exe.' }
& $Iscc 'packaging\CyAICodex.iss'
if ($LASTEXITCODE -ne 0) { throw 'Construction de l installateur impossible.' }
Write-Host 'Installateur disponible dans dist.'
