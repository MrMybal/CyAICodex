[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet('codex', 'claude-code', 'all')]
    [string]$Client = 'all',
    [ValidateSet('User', 'Project')]
    [string]$Scope = 'User',
    [string]$RootPath,
    [switch]$Update
)

$ErrorActionPreference = 'Stop'
$skillSource = Join-Path $PSScriptRoot 'cyaicodex'
$skillFiles = @('SKILL.md', 'LICENSE.txt')
foreach ($skillFile in $skillFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $skillSource $skillFile) -PathType Leaf)) {
        throw "Missing packaged file: $skillFile"
    }
}
if (-not $RootPath) {
    if ($Scope -eq 'User') { $RootPath = [Environment]::GetFolderPath('UserProfile') }
    else { $RootPath = (Get-Location).ProviderPath }
}
if (-not $RootPath) { throw 'Choose a profile or project root with -RootPath.' }
$installRoot = [IO.Path]::GetFullPath($RootPath)
$rootPrefix = $installRoot.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar

function Assert-PlainPath([string]$Path) {
    $candidate = [IO.Path]::GetFullPath($Path)
    while ($candidate) {
        if (Test-Path -LiteralPath $candidate) {
            $item = Get-Item -LiteralPath $candidate -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Linked destination rejected: $candidate. Copy the skill manually if this link is intentional."
            }
        }
        $parent = [IO.Path]::GetDirectoryName($candidate)
        if ($parent -eq $candidate) { break }
        $candidate = $parent
    }
}

$clients = if ($Client -eq 'all') { @('codex', 'claude-code') } else { @($Client) }
$plans = @()
foreach ($targetClient in $clients) {
    $relativePath = if ($targetClient -eq 'codex') { '.agents/skills/cyaicodex' } else { '.claude/skills/cyaicodex' }
    $destination = [IO.Path]::GetFullPath((Join-Path $installRoot $relativePath))
    if (-not $destination.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Destination escaped the selected root.' }
    Assert-PlainPath $destination
    if ((Test-Path -LiteralPath $destination) -and -not (Test-Path -LiteralPath $destination -PathType Container)) { throw "Not a directory: $destination" }
    $changes = @()
    foreach ($skillFile in $skillFiles) {
        $sourceFile = Join-Path $skillSource $skillFile
        $targetFile = Join-Path $destination $skillFile
        Assert-PlainPath $targetFile
        $exists = Test-Path -LiteralPath $targetFile
        if ($exists -and -not (Test-Path -LiteralPath $targetFile -PathType Leaf)) { throw "Not a file: $targetFile" }
        if ($exists -and (Get-FileHash -LiteralPath $sourceFile).Hash -eq (Get-FileHash -LiteralPath $targetFile).Hash) { continue }
        if ($exists -and -not $Update) { throw "Existing skill differs: $targetFile. Review it, then use -Update to keep a .previous backup and replace only the packaged files." }
        if ($exists) {
            $backupFile = $targetFile + '.previous'
            Assert-PlainPath $backupFile
            if ((Test-Path -LiteralPath $backupFile) -and -not (Test-Path -LiteralPath $backupFile -PathType Leaf)) { throw "Not a backup file: $backupFile" }
        }
        $changes += [pscustomobject]@{ Source = $sourceFile; Target = $targetFile; Exists = $exists }
    }
    $plans += [pscustomobject]@{ Client = $targetClient; Destination = $destination; Changes = $changes }
}

# Preflight every selected client before making any changes.
foreach ($plan in $plans) {
    if ($plan.Changes.Count -eq 0) { Write-Host "Already current: $($plan.Client)"; continue }
    if ($PSCmdlet.ShouldProcess($plan.Destination, 'Install CyAICodex agent Skill')) {
        New-Item -ItemType Directory -Path $plan.Destination -Force | Out-Null
        foreach ($change in $plan.Changes) {
            if ($change.Exists) { Copy-Item -LiteralPath $change.Target -Destination ($change.Target + '.previous') -Force }
            Copy-Item -LiteralPath $change.Source -Destination $change.Target -Force
        }
        Write-Host "Installed for $($plan.Client): $($plan.Destination)"
    }
}
Write-Host 'Available on the next turn/session after your client refreshes skills. Connect CyAICodex MCP separately; this installer does not edit client settings.'
