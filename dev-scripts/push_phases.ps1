param(
    [string]$RemoteUrl = 'https://github.com/yskhub/Agentic_Honey_Pot.git',
    [switch]$DryRun
)

function Run-Git([string]$cmd) {
    if ($DryRun) {
        Write-Host "DRY RUN: git $cmd"
    } else {
        Write-Host "-> git $cmd"
        Invoke-Expression ("git " + $cmd)
        $exit = $LASTEXITCODE
        if ($exit -ne 0) {
            Write-Error "git command failed (exit=$exit): git $cmd"
            return $false
        }
    }
    return $true
}

Write-Host "Push phases helper starting. Remote: $RemoteUrl"

if (-not (Test-Path -Path .git -PathType Container)) {
    if (-not (Run-Git 'init')) { exit 1 }
}

# Ensure branch is 'main'
if (-not (Run-Git 'branch --show-current')) { }

# Stage files and create initial commit if repository has no commits
if (-not $DryRun) {
    & git rev-parse --verify HEAD > $null 2>&1
    $hasHead = ($LASTEXITCODE -eq 0)
} else { $hasHead = $false }

Run-Git 'add -A'

if ($DryRun) {
    Write-Host 'DRY RUN: would commit changes with message.'
} else {
    if (-not $hasHead) {
        # create initial commit even if no changes
        Run-Git 'commit --allow-empty -m "chore: initial scaffold and phase files"'
    } else {
        $status = & git status --porcelain
        if ($status) { Run-Git 'commit -m "chore: initial scaffold and phase files"' } else { Write-Host 'No changes to commit.' }
    }
}

# Ensure current branch is named main
Run-Git 'branch -M main'

# Optional user config from environment
if ($env:GIT_USER_NAME) { Run-Git "config user.name \"$env:GIT_USER_NAME\"" }
if ($env:GIT_USER_EMAIL) { Run-Git "config user.email \"$env:GIT_USER_EMAIL\"" }


# Create phase branches
$branches = @('phase-1-scaffold','phase-2-agent','phase-3-outgoing-worker')
foreach ($b in $branches) {
    # create branch if not exists
    if (-not $DryRun) {
        $exists = (& git show-ref --verify --quiet refs/heads/$b); $code=$LASTEXITCODE
    }
    if ($DryRun -or ($LASTEXITCODE -ne 0)) {
        Run-Git "branch $b"
    } else {
        Write-Host "Branch $b already exists locally."
    }
}

# Tag v0.1.0 if not present
if ($DryRun) {
    Write-Host 'DRY RUN: git tag -a v0.1.0 -m "Phase 1: scaffold"'
} else {
    $tagExists = (& git tag -l v0.1.0).Trim()
    if (-not $tagExists) { Run-Git 'tag -a v0.1.0 -m "Phase 1: scaffold"' } else { Write-Host 'Tag v0.1.0 already exists.' }
}

# Add remote if missing
$remoteExists = & git remote get-url origin 2>$null; $rc=$LASTEXITCODE
if ($rc -ne 0) {
    Run-Git "remote add origin $RemoteUrl"
} else {
    Write-Host "Remote 'origin' already configured: $remoteExists"
}

# Push main, branches and tags
if ($DryRun) {
    Write-Host 'DRY RUN: would push main, branches and tags to origin.'
} else {
    if (-not (Run-Git 'push -u origin main')) { Write-Error 'Failed pushing main'; exit 2 }
    if (-not (Run-Git 'push origin --tags')) { Write-Error 'Failed pushing tags'; exit 3 }
    foreach ($b in $branches) {
        if (-not (Run-Git "push origin $b")) { Write-Warning "Failed pushing branch $b" }
    }
}

Write-Host 'Done.'
