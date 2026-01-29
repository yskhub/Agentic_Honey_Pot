Deployment

This document explains two simple deployment options: Docker Compose (quick) and systemd (production-friendly).

Docker Compose

1. Build and run locally:

```bash
# build and run (expose 8030)
docker-compose up --build -d
```

2. Environment variables:
- `API_KEY`, `ADMIN_API_KEY`, `OUTGOING_ENDPOINT` can be set in your shell or a `.env` file used by docker-compose.

3. Persistent data and logs:
- `data/` and `logs/` are mounted into the container by `docker-compose.yml`.

Systemd (recommended for a single Linux host)

1. Copy repository to the host (or git clone on the host):

```bash
# on host
git clone https://github.com/yskhub/Agentic_Honey_Pot.git /opt/agentic_honey_pot
cd /opt/agentic_honey_pot
```

2. Optional: create a dedicated system user:

```bash
sudo useradd -r -s /sbin/nologin sentinel
```

3. Create a Python virtual environment and install dependencies:

```bash
sudo python3 -m venv /opt/venv_agentic
sudo chown -R $USER:$USER /opt/venv_agentic
source /opt/venv_agentic/bin/activate
pip install -r requirements.txt
```

4. Edit `deploy/sentinel.service` to match the paths you used (WorkingDirectory, ExecStart, env vars).

5. Install and start the service (run as root):

```bash
sudo cp deploy/sentinel.service /etc/systemd/system/sentinel.service
sudo systemctl daemon-reload
sudo systemctl enable --now sentinel
sudo journalctl -u sentinel -f
```

6. Logs and data:
- Application writes audit logs to `logs/audit.log` and outgoing HTTP traces to `logs/outgoing_http.log` by default. Ensure these directories exist and are writable by the service user.

Operational notes

- Backups: copy `data/sentinel.db` regularly. sqlite is file-based.
- Migrations: use Alembic (`alembic/`) added to this repo. On the host, run `alembic upgrade head` after pulling schema changes.
- Security: store secrets in a secret manager or environment variables; avoid embedding them in the unit file for production.

Healthcheck

- The container image includes an HTTP healthcheck that probes the app's `/health` endpoint. The Dockerfile defines a `HEALTHCHECK` which expects a successful 2xx response from `http://127.0.0.1:8030/health`.
- Kubernetes, Docker Swarm, or systemd service monitors can use this endpoint to determine container/service health. Ensure your orchestration readiness/liveness probes target `/health` on port `8030`.

Audit HMAC key (`AUDIT_HMAC_KEY`) and rotation

- The audit log entries are HMAC-signed using the `AUDIT_HMAC_KEY` environment variable. This provides tamper-evidence for append-only audit logs. Keep the key secret (use a secret manager or encrypted env-store).
- Key rotation procedure (recommended):
	1. Generate a new secure key and store it in your secret manager as `AUDIT_HMAC_KEY_NEXT` or similar.
	2. Deploy the application with both `AUDIT_HMAC_KEY` (current) and `AUDIT_HMAC_KEY_NEXT` (new) set in the environment. The running code will verify entries using either key and sign new entries with the new key when you flip.
	3. After a transition period, update running instances to only use the new `AUDIT_HMAC_KEY` value.
	4. Revoke the old key from your secret manager and archive any required rotation audit trail notes.

Notes:
- Rotate keys regularly (90 days is a common baseline) and after any suspected compromise.
- Store rotation events in an external, immutable store (e.g., cloud KMS audit logs) if available.
- If you need assistance, I can add a small rotation helper script that performs the dual-key verify-and-sign transition.

JWT / JWKS admin authentication

- You can configure JWKS/OIDC-based admin authentication by setting the following environment variables:
	- `ADMIN_JWKS_URL`: URL to JWKS (e.g., https://your-issuer/.well-known/jwks.json)
	- `ADMIN_JWT_AUDIENCE`: (optional) expected audience claim
	- `ADMIN_JWT_ISSUER`: (optional) expected issuer claim
	- `ADMIN_JWKS_CACHE_TTL`: (optional) JWKS cache TTL in seconds (default 300)

- The app will fetch the JWKS, select the key by `kid` from the token header, and validate the token signature and (optionally) `aud` and `iss` claims. If JWKS is not configured, the app still accepts the existing `ADMIN_API_KEY` or a simple bearer token equal to that key.

If you'd like, I can:
- Add a `Makefile` to standardize build/deploy commands.
- Create a small Ansible playbook to automate the systemd deployment.
- Harden the systemd unit to use `ProtectSystem`, `NoNewPrivileges`, and other sandboxing options.

Local PR workflow

If you want to push phase branches and open PRs from your machine, follow these steps locally:

1. Authenticate with GitHub CLI:

```powershell
gh auth login
```

2. Push branches and tags (script will create branches/tags if missing):

```powershell
.\dev-scripts\push_phases.ps1
```

3. Create PRs for phase branches:

```powershell
.\dev-scripts\create_prs.ps1
```

Notes:
- `create_prs.ps1` uses the GitHub CLI (`gh`) to open PRs. Ensure your `gh` session has push/PR privileges on the target repo.
- Use `.env.example` as a template for local environment variables. Do not commit real secrets.

