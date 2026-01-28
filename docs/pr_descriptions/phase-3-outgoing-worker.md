Title: Phase 3 — Outgoing worker, Docker & Deployment

Summary:

- Add `outgoing_worker` DB-backed delivery worker and structured HTTP logging.
- Add `Dockerfile`, `docker-compose.yml`, systemd unit and install script for deployment.
- Add Alembic scaffolding, CI checks for migrations, and live E2E job.

Files of interest:
- `Dockerfile`, `docker-compose.yml`, `deploy/`, `alembic/`, `.github/workflows/ci.yml`

Notes:
- This PR finalizes operational readiness; please review Docker and migration scripts.
Files included in this phase (exact):

- Dockerfile
- docker-compose.yml
- deploy/sentinel.service
- deploy/install_service.sh
- .env.example
- alembic.ini
- alembic/env.py
- alembic/script.py.mako
- alembic/versions/ (placeholder)
- docs/migrations.md
- docs/deployment.md
- CHANGELOG.md
- .github/workflows/ci.yml (alembic check + live-e2e)
- dev-scripts/push_phases.ps1
- dev-scripts/create_prs.ps1
- docs/pr_descriptions/*

Notes:
 - This PR finalizes operational readiness; please review Docker, Alembic and CI changes.
