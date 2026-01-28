Param()

$workdir = Join-Path $PSScriptRoot '..\..'
$envFile = Join-Path $workdir '.env'
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

$logs = Join-Path $workdir 'logs'
if (-not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

$out = Join-Path $logs 'simulator.out.log'
$err = Join-Path $logs 'simulator.err.log'

Write-Output "Running judge simulator, stdout -> $out, stderr -> $err"

Start-Process -NoNewWindow -FilePath ".venv\Scripts\python.exe" -ArgumentList 'dev-scripts\judge_simulator.py' -RedirectStandardOutput $out -RedirectStandardError $err -WorkingDirectory $workdir -Wait

Write-Output "simulator finished"
