# Phase 5 — Judge Polish Checklist

Short checklist to prepare the UI and runbook for judge evaluation.

- [ ] Verify frontend exposes session list and session detail views.
- [ ] Ensure `GET /v1/session/{id}/result` returns extracted intelligence samples.
- [ ] Confirm no secrets are present in frontend builds or demos.
- [ ] Add clear judge instructions in `docs/JUDGE_RUNBOOK.md` (start backend, start frontend, start ngrok).
- [ ] Provide a one-click demo script `dev-scripts/judge_simulator.py` and verify it runs against default ports.
- [ ] Add export button in the UI to download session JSON (or provide endpoint `/v1/session/{id}/export`).
- [ ] Smoke-test the GUVI callback flow locally using `dev-scripts/run_e2e_local.py` and the CI smoke workflow.

Use this checklist to ensure the demo is judge-ready.
