Title: Phase 2 — Agent engine & Admin UI

Summary:

- Persona-driven agent implementation that auto-responds to routed messages.
- Persist agent messages and conversation state; add extraction storage.
- Add admin endpoints and a small SPA for managing outgoing messages (retry/delete/export).
- Add outgoing message DB model and worker scaffolding.

Files of interest:
- `backend/app/agent.py`, `backend/app/outgoing_worker.py`, `backend/app/routes.py`
- `backend/tests/` updated with agent and outgoing worker tests.

Notes:
- This PR depends on Phase 1 and adds critical persistence and operational controls.
Files included in this phase (exact):

- backend/app/agent.py
- backend/app/personas/honeypot_persona.json
- backend/app/routes.py (agent endpoints, admin endpoints, admin UI)
- backend/app/outgoing_worker.py
- backend/app/callback_queue.py (used by admin flows)
- backend/app/db.py (models modifications: Message, Extraction, OutgoingMessage, ConversationState updates)
- backend/tests/test_agent.py
- backend/tests/test_agent_persistence.py
- backend/tests/test_e2e_agent.py
- backend/tests/test_outgoing_worker.py
- dev-scripts/automated_e2e.py
- dev-scripts/automated_e2e_live_httpbin.py

Notes:
 - This PR depends on Phase 1 and adds critical persistence and operational controls.
