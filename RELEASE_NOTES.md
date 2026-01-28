Release notes (concise)

Version: v0.1.0 (draft)

Summary
- Phase 1: Project scaffold with FastAPI backend, detection rules, DB models, audit log and persistent callback queue.
- Phase 2: Agent engine, outgoing message queue and worker, admin UI for managing outgoing messages, and tests.
- Phase 3: Dockerization, deployment scripts (systemd), Alembic migrations scaffolding, CI checks and live E2E job.

How to tag a release locally

1. Ensure all tests pass and migrations are committed:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
alembic revision --autogenerate -m "release v0.1.0"  # review and commit if needed
alembic upgrade head
```

2. Create tag and push:

```powershell
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main --follow-tags
```

Notes
- Use a signed release process or CI pipeline to create signed tags for production releases.
