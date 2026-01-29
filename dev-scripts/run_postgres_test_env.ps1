<#
Runs a local Postgres container for integration tests and optionally runs pytest.

Usage:
  .\dev-scripts\run_postgres_test_env.ps1           # start postgres and set DATABASE_URL
  .\dev-scripts\run_postgres_test_env.ps1 -RunTests # start postgres, set DATABASE_URL and run tests
#>

param(
    [switch]$RunTests
)

$compose = "docker-compose.postgres.yml"
Write-Host "Starting Postgres via $compose..."
docker compose -f $compose up -d

Write-Host "Waiting for Postgres to listen on 127.0.0.1:5432..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    $res = Test-NetConnection -ComputerName '127.0.0.1' -Port 5432 -WarningAction SilentlyContinue
    if ($res -and $res.TcpTestSucceeded) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}

if (-not $ready) {
    Write-Error "Postgres did not become ready after waiting. Check 'docker compose ps' and container logs."
    exit 1
}

$env:DATABASE_URL = "postgresql+psycopg2://sentinel:sentinel_pass@127.0.0.1:5432/sentinel_db"
Write-Host "Exported DATABASE_URL for the current session: $env:DATABASE_URL"

if ($RunTests) {
    Write-Host "Running pytest against Postgres..."
    python -m pytest -q
}

Write-Host "Done. To stop the container: docker compose -f $compose down"
