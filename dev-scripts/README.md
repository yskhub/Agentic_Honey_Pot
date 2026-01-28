**Dev Scripts**

- **Purpose:** quick scripts to start the backend with verbose logs and to run the judge simulator for end-to-end verification.

- **Files:**
  - `start_server_verbose.ps1` — starts the FastAPI uvicorn server from the repository root and redirects stdout/stderr to `logs/uvicorn.out.log` / `logs/uvicorn.err.log`.
  - `run_simulator_verbose.ps1` — loads `.env` into the process environment, runs `dev-scripts/judge_simulator.py`, and redirects simulator logs to `logs/simulator.out.log` / `logs/simulator.err.log`.

- **Notes:**
  - These scripts do NOT persist environment variables to your user profile. Environment variables are set only for the spawned process.
  - If you need to run the simulator with a temporary override for API keys, run the simulator from `cmd.exe` with `set` (see examples below).

**Quick start (PowerShell)**

Run the server in background (writes logs to `logs/`):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\dev-scripts\start_server_verbose.ps1
```

Run the simulator (loads `.env` for the simulator process):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\dev-scripts\run_simulator_verbose.ps1
```

**Quick start (cmd.exe) — set env for the simulator process only**

```cmd
set API_KEY=test_client_key&& set ADMIN_API_KEY=test_admin_key&& .venv\Scripts\python.exe dev-scripts\judge_simulator.py
```

**Stop server**

```cmd
taskkill /IM python.exe /F
```

**Inspect logs**

```powershell
Get-Content -Path logs\uvicorn.out.log -Tail 200
Get-Content -Path logs\simulator.out.log -Tail 200
Get-Content -Path logs\audit.log -Tail 200
```

**If something fails**

- Ensure dependencies are installed in `.venv` (see project `requirements.txt`).
- Confirm `.env` exists at repo root and contains `API_KEY` / `ADMIN_API_KEY` / `GUVI_API_KEY`.

