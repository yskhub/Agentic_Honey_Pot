# Phase 2 — Agent MVP

Goal
Create a fully local agentic honeypot able to conduct believable multi-turn engagements with scripted personas and optional local LLM augmentation.

Tech stack (zero cost)
- Python
- Lightweight orchestration (custom planner) or LangChain (local)
- gpt4all / llama.cpp / local Hugging Face quantized model (optional)
- Redis (local docker) or in-memory cache for sessions
- FastAPI backend (extend phase 1)

Prerequisites
- Phase 1 complete (basic backend, DB, ingestion)
- Optional: local LLM binaries downloaded & tested

Step-by-step tasks (full details)

1. Agent architecture & interfaces (1–2 hours)
   - Define agents as modules:
     - `planner` (decides next move)
     - `conversation_agent` (generates reply)
     - `memory` (short-term info store)
     - `safety_agent` (applies hard/soft rules)
   - Define interfaces in `backend/agent/interfaces.py`.

2. Persona configuration (30–60 minutes)
   - Create `backend/agent/personas/elderly.json`, `student.json`, `jobseeker.json` with keys:
     - `persona_id`, `name`, `age_range`, `tone`, `greeting_templates`, `fallback_templates`, `disallowed_phrases`
   - Example template contains variable placeholders like `{name}`, `{bank}`, to be substituted.

3. Scripted dialogue flows (4–6 hours)
   - For each common scam scenario (bank-impersonation, UPI-payment request, job-scam), author a decision tree:
     - Node format: trigger (regex/intent), response templates, next actions (ask for info, feign confusion, stall)
   - Store trees as JSON in `backend/agent/templates/`.
   - Implement executor `backend/agent/scripted_engine.py` that runs trees deterministically.

4. Session lifecycle & routing (2–4 hours)
   - Extend `/v1/message` logic:
     - If `scamProbability` > threshold (e.g., 0.5), set `routeToAgent`.
     - Agent loop:
       - Load session memory (last N messages)
       - Planner decides: scripted reply or LLM call
       - Safety agent validates content
       - Persist agent reply as `Message` and return to caller.
   - Implement session timeout and max messages per session.

5. Memory & storage (1–2 hours)
   - Implement `backend/agent/memory.py`:
     - In-memory ring buffer per session (size configurable); optionally Redis if installed.
     - Summary storage: key facts (payment methods, phone numbers) with provenance.

6. Optional local LLM integration (2–6 hours)
   - Add `backend/agent/llm_wrapper.py` that:
     - Abstracts provider (gpt4all, llama.cpp, or server-side Google GenAI if later allowed).
     - Applies timeouts and token limits.
     - Returns structured reply and optional extracted entities.
   - Always fall back to scripted reply on model failure.

7. Safety & failover (1–2 hours)
   - Safety agent enforces:
     - No financial instructions; redact any agent content that might enable scams.
     - Auto-terminate on escalation triggers (multiple payment identifiers).
   - Logging: capture decision trace (why planner chose a reply).

8. Deliverables & testing (2 hours)
   - Demo script `dev-scripts/run_agent_demo.py` that simulates a scammer and logs the entire session.
   - Documentation: "How to run with scripted flows" and "How to enable local LLM".

Performance note
- Prefer scripted templates for the hackathon initial submission to ensure reliable scoring and avoid slow LLM calls.

