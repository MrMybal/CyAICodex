$ErrorActionPreference = 'Stop'
$clientFolder = Join-Path $PSScriptRoot 'data\local-clients'
& npm.cmd install --prefix $clientFolder '@anthropic-ai/claude-code@2.1.270' 'opencode-ai@1.18.30'
if ($LASTEXITCODE -ne 0) { throw 'Installation des clients locaux impossible. Vérifiez Node.js et npm.' }
Write-Host 'Clients installés. Ouvrez CyAICodex > Paramètres pour vérifier et connecter vos comptes.'
