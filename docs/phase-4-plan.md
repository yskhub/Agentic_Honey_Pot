Phase 4 — Extension & Hardening
================================

Goals
-----
- Expand capabilities beyond the initial honeypot: durable telemetry export, richer extraction, scale and observability.
- Harden production deployment and DB migration workflow (Postgres + Alembic revisions committed).
- Add integration adapters and a small orchestration layer for ingestion and export.

Planned Workstreams
-------------------
1. Persistence and Migrations
   - Add Postgres support and connection configuration in `DATABASE_URL`.
   - Produce audited Alembic migration revisions and commit them to `alembic/versions/`.
   - Add a small migration verification script for CI to run before deploy.

2. Export & Integrations
   - Implement an export adapter interface and initial exporter (GUVI callback, S3/CSV, external telemetry API).
   - Make outgoing worker idempotent and add exponential backoff + jitter for retries.

3. Extraction & Intelligence
   - Add an extensible `extractors/` package for rule-based + ML-assisted extraction.
   - Start with deterministic extractors (phone, upi, urls, btc) and provide a model hook for later upgrades.

4. Observability & Ops
   - Add Prometheus metrics endpoint and counters for messages, detections, outgoing attempts, and failures.
   - Convert outgoing HTTP traces to structured JSON logs and add a rolling file/Logstash-friendly output.
   - Improve Dockerfile (non-root user, smaller base image, multi-stage, healthcheck) and add `Makefile` targets.

5. Security & Auth
   - Harden systemd unit: `NoNewPrivileges`, `ProtectSystem=full`, and runtime file access minimization.
   - Validate JWKS caching TTL; add automated JWKS refresh logic with backoff.

6. Tests & CI
   - Add integration tests that target Postgres using a docker-compose test profile or GitHub Actions service container.
   - Keep the existing Alembic autogenerate check; require migrations when schema changes are introduced.

Next Immediate Steps (I will do if you confirm)
-----------------------------------------------
- Create `backend/phase4/` scaffold (exporter interface, extractors package, metrics stub).
- Add Postgres connection config and a `dev-scripts/run_postgres_test_env.ps1` for local integration testing.
- Create initial PR describing Phase‑4 scope and files to be added.

Tell me which of the immediate steps you want me to start first and I will scaffold it now.
