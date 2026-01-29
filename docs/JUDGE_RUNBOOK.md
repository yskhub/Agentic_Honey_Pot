# Judge Runbook — Secrets & SSE Token Rotation

This document explains how to rotate `ADMIN_SSE_SECRET`, distribute judge credentials securely for demos, and how the short-lived SSE token flow works.

1) Rotation of `ADMIN_SSE_SECRET`
- Generate a new random secret (at least 32 bytes hex). Example (on Linux/macOS):
  ```bash
  python - <<'PY'
  import secrets
  print(secrets.token_hex(32))
  PY
  ```
- Stop the backend and set the new secret in the environment: `ADMIN_SSE_SECRET=...`.
- Restart the backend. Existing tokens will be invalidated (they were signed with the old secret).

2) Distributing judge credentials securely
- For small demos, use a short-lived shared judge secret (`JUDGE_SHARED_SECRET`) distributed over a secure channel (e.g., a one-time Slack DM, a password-protected PDF, or using a judge portal).
- Do NOT embed the secret in public URLs or the frontend source. Judges should paste the secret into the UI prompt when requested.
- For higher security, create per-judge credentials and host a small authentication portal that returns a short-lived `x-judge-token` for the browser.

3) How the SSE token flow works
- Judges or the Streamlit server request a short-lived token using:
  - `POST /admin/ui/token` (requires `x-api-key: ADMIN_API_KEY`) — server-side (admin only)
  - or `POST /admin/ui/token-proxy` (requires `x-judge-token` header or Basic auth with password `JUDGE_SHARED_SECRET`) — judge-facing proxy
- The token is an HS256 JWT signed with `ADMIN_SSE_SECRET` and normally valid for `ADMIN_SSE_TOKEN_TTL` seconds (default 120).
- The browser opens `EventSource('/admin/ui/sse/session/{id}?token=...')`. The SSE endpoint validates the token and streams new messages.

4) Best practices
- Use HTTPS in production. Do not expose `ADMIN_API_KEY` or `ADMIN_SSE_SECRET` to clients.
- Prefer the judge proxy flow (`JUDGE_SHARED_SECRET`) rather than giving judges the full `ADMIN_API_KEY`.
- Rotate secrets periodically and after each event if you suspect leakage.

5) Judge login page (browser-friendly)
- A lightweight frontend page is available at `/judge-login` (Next.js) which POSTs to `/admin/ui/judge-login` with `username` and `password`.
- Configure per-judge credentials via the `JUDGE_USERS` env var using `user:pass` pairs (comma-separated). Example: `JUDGE_USERS="alice:pw1,bob:pw2"`.
- Successful login returns `{token, expires_in}`; the page stores this token in `sessionStorage` for subsequent SSE usage.

Note: this is meant for low-risk demo environments. For production, prefer a hardened auth portal and short-lived judge proxy tokens.
