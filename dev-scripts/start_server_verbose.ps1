Param()

$envFile = Join-Path $PSScriptRoot '..\..\.env'
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -and $_ -notmatch '^#') {
            $parts = $_ -split '='
            if ($parts.Length -ge 2) {
                $name = $parts[0].Trim()
                $value = $parts[1..($parts.Length-1)] -join '='
                Set-Item -Path "env:$name" -Value $value
            }
        }
    }
}

$workdir = Join-Path $PSScriptRoot '..\..'
$logs = Join-Path $workdir 'logs'
if (-not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

$out = Join-Path $logs 'uvicorn.out.log'
$err = Join-Path $logs 'uvicorn.err.log'

Write-Output "Starting uvicorn with debug logging, stdout -> $out, stderr -> $err"

Start-Process -NoNewWindow -FilePath ".venv\Scripts\python.exe" -ArgumentList '-m','uvicorn','backend.app.main:app','--reload','--port','8000','--log-level','debug' -RedirectStandardOutput $out -RedirectStandardError $err -WorkingDirectory $workdir -PassThru

Write-Output "uvicorn started"
