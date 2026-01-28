# Phase 5 — Dashboard & UI

Goal
Provide a judge‑impressive UI to visualize live sessions, extracted intelligence, and the honeypot console.

Tech stack (zero cost)
- Next.js (Vercel free) or static demo pages
- Tailwind CSS
- Reuse `sentinel-agentic-honey-pot` React components where possible
- Streamlit for internal analyst tools (optional)
- ngrok for exposing local backend during demo

Step-by-step tasks (full details)

1. Frontend wiring (2–4 hours)
   - Create `frontend/` Next.js app or reuse repository UI.
   - Replace client-side LLM calls with server `/v1/message` and `/v1/finalize`.
   - Implement API key entry screen (prompt user to paste server API key for demo).

2. Session Console (3–5 hours)
   - Implement session list view showing sessions with statuses (active, terminated).
   - Session detail view shows messages timeline, extracted entities with confidence scores, and controls:
     - Terminate Session
     - Export Session (JSON)
     - Mark for Review (flag)

3. Intelligence Vault & timeline (2–4 hours)
   - Aggregate extractions by type and show counts, recent sessions, and sample payloads.
   - Allow filtering by scam type and export as CSV/JSON.

4. Live updates & demo polish (2–4 hours)
   - Use polling or SSE to display live messages (fake streaming for demo if SSE not available).
   - Add light/dark toggle, minimal animations, and copy/export buttons.

5. Secure demo access (1 hour)
   - Do not embed secrets in frontend.
   - Provide instructions in README for judges describing the ephemeral API key and how to test.

6. Deployment & judge instructions (1–2 hours)
   - Deploy frontend to Vercel free or run locally and expose with ngrok.
   - Create `docs/JUDGE_RUNBOOK.md` with exact steps to:
     - Start backend
     - Start frontend
     - Start ngrok and provide URL to judges
     - Run `dev-scripts/judge_simulator.py` to validate callback

Deliverables
- Working judge-ready UI, export functions, runbook and demo checklist.

