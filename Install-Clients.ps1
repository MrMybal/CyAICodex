$ErrorActionPreference = 'Stop'
$clientFolder = Join-Path $PSScriptRoot 'data\local-clients'
& npm.cmd install --prefix $clientFolder '@anthropic-ai/claude-code@2.1.270' 'opencode-ai@1.18.30'
if ($LASTEXITCODE -ne 0) { throw 'Local client installation failed. Check Node.js and npm.' }
Write-Host 'Clients installed. Open CyAICodex > Settings to check and connect your accounts.'
