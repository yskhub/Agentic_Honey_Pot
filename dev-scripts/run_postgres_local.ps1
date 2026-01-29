<##
Run Postgres locally with Docker Compose and execute pytest against it.

Usage:
  .\dev-scripts\run_postgres_local.ps1

Requirements:
  - Docker and docker-compose available in PATH
  - Python virtualenv with deps (or use system Python)

#>
Set-StrictMode -Version Latest

$composeFile = "docker-compose.postgres.yml"
Write-Host "Starting Postgres via docker-compose ($composeFile)"
docker compose -f $composeFile up -d

Write-Host "Waiting for Postgres to become ready..."
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
  try {
    docker compose -f $composeFile exec -T postgres pg_isready -U sentinel -d sentinel_db
    if ($LASTEXITCODE -eq 0) { break }
  } catch {
    # docker or pg_isready not available yet
  }
    Start-Sleep -Seconds 2
    $attempt++
    Write-Host "Attempt $attempt/$maxAttempts..."
}

if ($attempt -ge $maxAttempts) {
    Write-Error "Postgres did not become ready in time"
    exit 1
}

Write-Host "Postgres is ready. Running pytest against Postgres..."
$env:DATABASE_URL = 'postgresql+psycopg2://sentinel:sentinel_pass@127.0.0.1:5432/sentinel_db'
python -m pytest -q

Write-Host "Tests finished. Tearing down docker-compose services..."
docker compose -f $composeFile down -v

exit 0
