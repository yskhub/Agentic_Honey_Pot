# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Phase 3 — Dockerization & Deployment (in progress)
- Added `Dockerfile` and `docker-compose.yml` for local/container deployments.
- Added systemd unit `deploy/sentinel.service` and `deploy/install_service.sh` for single-host installs.
- Added `docs/deployment.md` deployment instructions and `docs/migrations.md`.

### Phase 2 — Agent, Outgoing Worker & Admin UI (completed)
- Implemented rule-based detector and persona-driven agent (`backend/app/agent.py`).
- Added `OutgoingMessage` queue and `backend/app/outgoing_worker.py` to deliver or simulate outgoing HTTP requests; structured traces to `logs/outgoing_http.log`.
- Added admin endpoints and SPA at `GET /admin/ui/outgoing` with CSV export, retry and delete controls.
- Persisted messages, extractions, conversation state and outgoing queue in SQLite via SQLAlchemy.

### Phase 1 — Project scaffold (completed)
- FastAPI scaffold, DB models, audit append-only HMAC log, file-based persistent callback queue.
- Dev scripts under `dev-scripts/` for E2E testing and helpers.

## How to release

1. Ensure all tests pass: `pytest -q`.
2. Update `alembic/` migrations as needed and commit them.
3. Tag the release (example): `git tag -a v0.1.0 -m "Release v0.1.0"` and `git push --tags`.
