Title: Phase 1 — Project scaffold

Summary:

- Add FastAPI backend scaffold with core models and detection logic.
- Add append-only HMAC audit log and file-based callback queue for reliability.
- Add initial dev scripts and unit tests for detector.

Files of interest:
- `backend/app/` (models, routes, detector, audit, callback_queue)
- `dev-scripts/` (test harnesses)
Files included in this phase (exact):

- backend/app/schemas.py
- backend/app/db.py
- backend/app/audit.py
- backend/app/callback_queue.py
- backend/app/main.py
- backend/app/detector.py
- backend/app/rate_limit.py
- backend/app/auth.py (initial auth helpers)
- backend/app/__pycache__ (compiled artifacts)
- backend/app/personas/ (persona starter files)
- dev-scripts/run_tests.py
- dev-scripts/judge_simulator.py
- dev-scripts/start_uvicorn_programmatic.py
- dev-scripts/*.ps1 (PowerShell helpers)
- backend/tests/test_detector.py
- .env.template

Notes:
 - This PR creates the base project and should be merged before subsequent phases.
