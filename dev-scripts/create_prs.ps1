param(
    [string]$Repo = 'yskhub/Agentic_Honey_Pot',
    [string]$Base = 'main'
)

function Ensure-Gh() {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Error 'gh (GitHub CLI) not found. Install from https://cli.github.com/'
        exit 1
    }
}

Ensure-Gh

$branches = @(
    @{ name = 'phase-1-scaffold'; title = 'Phase 1: scaffold'; body = 'Initial scaffold and phase files.' },
    @{ name = 'phase-2-agent'; title = 'Phase 2: agent'; body = 'Persona + agent implementation.' },
    @{ name = 'phase-3-outgoing-worker'; title = 'Phase 3: outgoing worker'; body = 'Outgoing message worker and deployment assets.' }
)

foreach ($b in $branches) {
    $name = $b.name
    # Create PR (if not exists)
    Write-Host "Creating PR for $name -> $Base"
    gh pr view --repo $Repo --head $name --json number -q .number 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PR already exists for $name"
        continue
    }
    gh pr create --repo $Repo --base $Base --head $name --title "$($b.title)" --body "$($b.body)"
}

Write-Host 'Done.'
