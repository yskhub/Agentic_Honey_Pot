# Phase 4 — Ethics & Safety

Goal
Ensure safety: enforce guardrails, provide an auditable log, implement kill-switches, and document legal/ethics checklists.

Tech stack (zero cost)
- Python
- Rule-based filters
- HMAC signing (`hmac`, `hashlib`)
- Simple admin API key controls via `.env`

Step-by-step tasks (full details)

1. Policy & checklist (30–60 minutes)
   - Add `POLICIES.md` describing:
     - No real financial transactions
     - No impersonation of specific real persons
     - Data retention policy
     - Consent and jurisdiction notes
   - Add "pre-demo checklist" requiring human sign-off.

2. Hard rules (1–2 hours)
   - Implement `backend/safety/safety_rules.py` to:
     - Block outgoing replies containing instructions to transfer money.
     - Block sharing of PII (SSN, full bank details).
     - Identify escalation patterns (multiple payment channels requested).
   - Hook safety checks into agent output flow.

3. Kill-switch & escalation (1 hour)
   - `POST /v1/admin/terminate-session` — requires admin API key.
   - Auto-terminate triggers:
     - Extraction finds phone + UPI + bank in same session
     - Agent or incoming message explicitly mentions illegal acts
   - On termination: mark session closed, prepare GUVI final payload, and call finalize endpoint (server-side).

4. Audit & tamper-evident logs (2 hours)
   - Append-only log file format:
     - Each event: timestamp, event_type, payload_json, HMAC signature (server secret)
   - Implement rotation and export function that zips logs and includes verification instructions.

5. Privacy, retention & redaction (1–2 hours)
   - Implement redaction policy on stored raw messages: mask numbers > 6 digits in stored text unless required for evidence.
   - Provide `dev-scripts/purge_old_logs.py` to remove old raw logs per retention policy.

6. Red-team scripts & testing (2 hours)
   - Create `redteam/` with test cases:
     - Rapid UPI requests
     - Social engineering attempts with names/orgs
     - Attempts to coax the agent into revealing system details
   - Run these before any public demo.

Deliverables
- `POLICIES.md`, `safety_rules.py`, kill-switch endpoint, HMAC log export tool.

