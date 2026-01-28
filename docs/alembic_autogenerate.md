Alembic Autogenerate: Guidance
=================================

Purpose
-------
This document explains how to generate and review Alembic autogenerate revisions locally. The repository's CI will fail if schema changes are present without committed migration files.

Quick steps
-----------
1. Activate your Python virtual environment (or rely on the project's `.venv`):

```powershell
# if using the repo venv
. .\.venv\Scripts\Activate.ps1

# or activate your environment manually
# python -m venv .venv ; . .venv\Scripts\Activate.ps1
```

2. Ensure `DATABASE_URL` points to the target database you want to autogenerate against. For local dev using SQLite (safe for autogenerate), set:

```powershell
$env:DATABASE_URL = "sqlite:///data/sentinel.db"
```

Or for Postgres test environment (if running `docker-compose.postgres.yml`):

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://sentinel:sentinel_pass@127.0.0.1:5432/sentinel_db"
```

3. Run the helper script to generate a revision (it will install `alembic` into the venv if missing):

```powershell
.\dev-scripts\generate_alembic_revision.ps1 -Message "initial schema"
```

4. Review the generated file under `alembic/versions/` carefully. Autogenerate is a best-effort — inspect `upgrade()` and `downgrade()` for correctness.

5. If the migration looks correct, commit the new revision file and push. CI's alembic autogenerate check will then pass.

Notes & Troubleshooting
-----------------------
- If autogenerate reports no changes, there may be no schema drift. If CI still fails, verify your local imports and `DATABASE_URL` target.
- For Postgres autogenerate, ensure the target DB has the current production schema state (or run against a clean DB representing the expected state).
- Always review generated migrations; autogenerate can miss complex changes (e.g., data migrations, enum changes).
