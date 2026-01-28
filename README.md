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

- `dev-scripts/automated_e2e.py` — starts a mock receiver, sets `OUTGOING_ENDPOINT` and runs an in-process E2E using TestClient.
- `dev-scripts/automated_e2e_live_httpbin.py` — sends outgoing messages to `https://httpbin.org/post` to verify remote delivery.
- `dev-scripts/judge_simulator.py` — simple simulator to post example messages.

Admin UI

- `GET /admin/ui/outgoing` — small single-page admin UI (requires `ADMIN_API_KEY` header) to search, retry, delete and export outgoing messages.

Logs

- Audit events: `logs/audit.log` (append-only, HMAC-signed lines).
- Outgoing HTTP traces: `logs/outgoing_http.log` (structured JSON lines).

Notes

- For reliable outgoing delivery, set `OUTGOING_ENDPOINT` before the app starts so the worker picks it up.
- Use `ADMIN_API_KEY` as the `x-api-key` header when calling admin endpoints.

If you want, I can add Docker files or CI job steps to run the live E2E in CI.
