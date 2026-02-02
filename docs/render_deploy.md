# Deploying to Render via GitHub

This document describes a minimal setup to deploy the project to Render using GitHub.

1. Connect your GitHub repo to Render
   - In the Render dashboard, create a new Web Service and connect the repository `yskhub/Agentic_Honey_Pot`.
   - Use `Docker` as the environment and point to the `Dockerfile` at the repository root.
   - For the worker, create a separate Service (Background Worker) pointing to the same repo and `Dockerfile` and set the start command to `python -m backend.app.outgoing_worker`.

2. Create a managed Postgres database on Render
   - In Render, create a Postgres database and note its `DATABASE_URL`.
   - Add it to Render service environment variables as `DATABASE_URL`.

3. Required secrets (in GitHub repository Settings → Secrets):
   - `RENDER_API_KEY`: Render API key (used by CI to trigger deploys). Create in Render account settings.
   - `RENDER_SERVICE_ID`: Render service ID for the web service (used by CI to create a deploy)
   - `RENDER_SERVICE_ID_WORKER`: (optional) worker service ID if you want CI to trigger worker deploy separately.
   - `AUDIT_HMAC_KEY`, `API_KEY`, `ADMIN_API_KEY`: application secrets — **do not** commit these in Git.

4. Migrations
   - After the DB is provisioned, run migrations:
     - From your local machine: `alembic upgrade head --raiseerr -x db_url=<DATABASE_URL>` (or set `DATABASE_URL` env var)
     - Or create a Render one-off job that runs `alembic upgrade head` against the managed DB.

5. CI workflow
   - A GitHub Action `.github/workflows/render-deploy.yml` has been added to run tests on `push` to `main` and trigger a Render deploy via the API if `RENDER_API_KEY` and `RENDER_SERVICE_ID` secrets are set.

6. Logs and persistence
   - Render instances have ephemeral disks; forward logs to an external provider or use Render's log streaming. Do not rely on the local `logs/` directory for long-term storage.

7. Smoke tests
   - After deployment, run your smoke tests against the staging URL to verify endpoints, audit signing, and worker processing.

If you want, I can:
- Add an additional workflow step to run `alembic upgrade head` automatically (requires a safe way to provide DB credentials), or
- Create a small `renderctl` helper script that calls Render API to run one-off jobs for migrations.

Tell me which option you prefer and I will implement it.
