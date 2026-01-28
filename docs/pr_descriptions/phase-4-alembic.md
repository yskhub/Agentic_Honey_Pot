Phase 4 — Alembic migrations: initial autogenerate

Summary
-------
This PR adds an initial Alembic autogenerate revision and makes the Alembic
environment and template robust for CI and local generation.

Changes included
- `alembic/versions/2e3418fca3f1_autogen_20260128173310_initial_schema.py`: generated autogenerate revision (empty upgrade/downgrade — please review).
- `alembic/env.py`: made logging setup tolerant to missing logger sections.
- `alembic/script.py.mako`: fixed Mako template and added revision identifier placeholders.
- `dev-scripts/generate_alembic_revision.ps1`: helper script to generate autogenerate revisions locally.
- `docs/alembic_autogenerate.md`: guidance for generating/reviewing Alembic revisions.

Notes for reviewer
------------------
- Please review the generated migration under `alembic/versions/` to ensure the
  `upgrade()` and `downgrade()` operations correctly capture intended schema changes.
- If the migration needs non-trivial data changes or manual edits, adjust the file
  before merging.

How to test locally
-------------------
1. Activate venv and set `DATABASE_URL` to a dev DB (sqlite or Postgres test).
2. Run `.\dev-scripts\generate_alembic_revision.ps1 -Message "review"` and inspect.
3. Run `alembic upgrade head` on the dev DB to apply the migration.
