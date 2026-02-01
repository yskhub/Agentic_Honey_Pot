# Agentic Honey Pot

![CI](https://github.com/yskhub/Agentic_Honey_Pot/actions/workflows/ci.yml/badge.svg)
![Postgres integration](https://github.com/yskhub/Agentic_Honey_Pot/actions/workflows/integration-postgres.yml/badge.svg)

This repository contains the SentinelTrap honeypot (FastAPI) with phased development. See `docs/` for deployment and operational notes.
# Agentic Honey Pot — Backend

Quick start (dev)

1. Create and activate a virtual environment and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the server (programmatic runner uses `DEV_SERVER_PORT` or `8030`):

```powershell
# start with an OUTGOING_ENDPOINT for real delivery (optional)
$env:OUTGOING_ENDPOINT = 'https://httpbin.org/post'
$env:API_KEY = 'test_server_key'
$env:ADMIN_API_KEY = 'test_admin_key'
$env:DEV_SERVER_PORT = '8030'
python dev-scripts/start_uvicorn_programmatic.py
```

Or use the PowerShell helper `dev-scripts/start_uvicorn_uvicorn_8030.ps1`.

3. Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Developer utilities


Admin UI


Logs


Notes


If you want, I can add Docker files or CI job steps to run the live E2E in CI.
