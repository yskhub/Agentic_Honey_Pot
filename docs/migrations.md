Alembic migrations

This project uses Alembic for schema migrations.

Quick guide

1. Install dependencies (inside your venv):

```powershell
pip install -r requirements.txt
```

2. Initialize and generate first revision (from repo root):

```powershell
# create an autogenerate revision
alembic revision --autogenerate -m "Initial schema"

# apply migrations
alembic upgrade head
```

Notes

- Alembic reads `sqlalchemy.url` from `alembic.ini`. For development you can edit that file, or set `DATABASE_URL` in the environment and update the `alembic.ini` before running.
- `alembic/env.py` imports the SQLAlchemy `Base` from `backend.app.db` so autogenerate will pick up models declared there.
- In CI you can run `alembic upgrade --sql` to inspect generated SQL before applying.

Recommendation

- For production, use a controlled migration process and do not rely on autogenerate to make schema changes without review.
