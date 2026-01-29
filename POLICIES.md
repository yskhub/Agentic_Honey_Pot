# Policies and Safety Checklist

This file documents core safety and ethics policies for running the agentic honeypot.

1. No real financial transactions
   - The system must never initiate or facilitate actual money transfers.
   - Agents must not provide step-by-step instructions to move funds or UPI flows.

2. No sharing of PII
   - Do not output full bank account numbers, SSNs, or other sensitive identifiers.
   - Stored raw messages containing long digit sequences should be masked when possible.

3. Kill-switch and escalation
   - Admin can terminate a session via `POST /v1/admin/terminate-session`.
   - Auto-termination triggers: phone + UPI + explicit payment request in same session.

4. Audit logging and tamper-evidence
   - All important events are appended to the audit log with an HMAC signature.
   - `backend/app/audit.py` implements signing and verification helpers.

5. Retention and redaction
   - Raw logs should be redacted for PII on export; numeric identifiers longer than 6 digits must be masked.
   - Implement a retention policy and a purge script for old logs.

6. Demo & judge path
   - No paid APIs or cloud LLMs in judge path; provide deterministic scripted fallbacks.
   - Do not embed secrets in frontends or public demos.

Checklist before demo
- Ensure `AUDIT_HMAC_KEY` is set for non-dev runs.
- Verify the admin API key is configured and known to judges.
- Run red-team tests in `dev-scripts/` and confirm safety rules block dangerous outputs.
