PR summary — phase-4/alembic-initial

- Added concrete Alembic initial migration creating core tables and indexes (`alembic/versions/2e3418fca3f1_autogen_20260128173310_initial_schema.py`).
- Stamped the existing local DB to that revision to avoid re-applying tables created by the app's `init_db()` during testing.
- Created a merge revision to unify two heads (`0001_initial` and `2e3418fca3f1`) into `9f19a59fa239` so Alembic history is linear for CI checks.
- Added `dev-scripts/rotate_audit_key.sh` to assist with dual-key `AUDIT_HMAC_KEY` rotation; see `dev-scripts/rotate_audit_key.sh` for usage.

Requested reviewers: @username1, @username2

Notes for reviewers:
- Please confirm the created tables and column types match expectations for Postgres targets (this migration is written in generic SQLAlchemy/SA terms, but small type adjustments may be needed for PG-specific conventions).
- If you prefer removing the placeholder `0001_initial.py` file instead of merging, let me know and I can delete it and push a follow-up.

Suggested command to run locally before merging:

```bash
# run migrations against local DB
alembic upgrade heads

# or to apply a specific revision
alembic upgrade 9f19a59fa239
```
