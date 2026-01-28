<#
Helper to create an Alembic autogenerate revision using the project's virtualenv.

Usage:
  .\dev-scripts\generate_alembic_revision.ps1            # creates autogen revision
  .\dev-scripts\generate_alembic_revision.ps1 -Message "describe changes"

The script will:
- Activate the repo venv if present
- Ensure `alembic` is available (install into venv if needed)
- Run `alembic revision --autogenerate -m "autogen:<timestamp> - Message"`
- Print the path(s) of any created files under `alembic/versions/` for review

IMPORTANT: Review the generated migration file before committing. The CI checks will fail if autogenerate diffs are present.
#>

param(
    [string]$Message = "autogen",
    [switch]$InstallIfMissing = $true
)

function Activate-Venv {
    $venv = Join-Path $PSScriptRoot "..\.venv\Scripts\Activate.ps1"
    if (Test-Path $venv) {
        . $venv
        return $true
    }
    return $false
}

Write-Host "Generating alembic autogenerate revision..."
$activated = Activate-Venv
if (-not $activated) {
    Write-Warning "No venv activate script found at .venv; ensure Python env is available in PATH or activate manually."
}

# Ensure alembic present
try {
    python -c "import alembic" 2>$null
} catch {
    if ($InstallIfMissing) {
        Write-Host "Installing alembic into venv..."
        python -m pip install alembic
    } else {
        Write-Error "Alembic not found in Python environment. Run 'pip install alembic' or set -InstallIfMissing.";
        exit 1
    }
}

# Compose message with timestamp
$ts = Get-Date -Format yyyyMMddHHmmss
$fullmsg = "autogen:$ts - $Message"

# Run alembic autogenerate
alembic revision --autogenerate -m "$fullmsg"

# Show created/modified files under alembic/versions
Write-Host "Listing alembic/versions files (most recent first):"
Get-ChildItem -Path "alembic/versions" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | ForEach-Object { Write-Host $_.FullName }

Write-Host "Done. Review the generated file(s) and commit when ready."
