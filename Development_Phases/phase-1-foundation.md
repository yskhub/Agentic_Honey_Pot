# Phase 1 — Foundation

Goal
Build the ingestion, core data model, and a reliable zero‑cost scam intent detector. Produce a runnable local FastAPI service with a rule‑based classifier and SQLite storage.

Tech stack (zero cost)
- Python 3.10+
- FastAPI + Uvicorn
- SQLite (local file) + SQLAlchemy
- scikit-learn (TF‑IDF + simple classifier) or rule-based fallback
- spaCy (en_core_web_sm)
- python-dotenv, requests
- git + GitHub (public repo)
- Streamlit (internal demo)
- ngrok/localtunnel (temporary public URL)

Prerequisites (what you need)
- Windows or Linux dev machine with Python 3.10+
- Git and a GitHub account (public repo)
- PowerShell or bash for running scripts

Step-by-step tasks (full details)

1. Repo & environment setup (1–2 hours)
   - Create repo root and initial folders:
     - `backend/`, `backend/app/`, `data/`, `dev-scripts/`, `frontend/`
   - Create `requirements.txt`:
     - fastapi
     - uvicorn[standard]
     - sqlalchemy
     - pydantic
     - python-dotenv
     - requests
     - scikit-learn
     - joblib
     - spacy
     - phonenumbers
   - Commands:
     - `python -m venv .venv`
     - `.venv\Scripts\activate`
     - `pip install -r requirements.txt`
   - Create `.gitignore` (ignore `.venv`, `.env`, `__pycache__`, `/data/*.db`).

2. Define scam taxonomy & data manifest (30–60 minutes)
   - Create `data/scam_taxonomy.json` with entries:
     - id, name, example_keywords, description
   - Create `data/sources.json` to record dataset URLs and licenses.
   - Create `data/labels.csv` (columns: text,category,source) with at least 200 rows for initial tests (synthesized if necessary).

3. Minimal code layout (1 hour)
   - Files to create:
     - `backend/app/main.py` — FastAPI app and startup hooks
     - `backend/app/schemas.py` — Pydantic models mirroring PRD message types
     - `backend/app/auth.py` — `x-api-key` header validator
     - `backend/app/db.py` — SQLite SQLAlchemy engine and models (sessions, messages, extractions)
     - `backend/app/routes.py` — `/health`, `/v1/message`, `/v1/admin/*`
     - `backend/app/detector.py` — rule-based heuristics
     - `dev-scripts/test_ingest.py` — POST sample messages
   - Implement basic logging to `logs/`.

4. Implement rule-based detector (2–4 hours)
   - Create `backend/app/detector.py`:
     - Keyword lists from `scam_taxonomy.json`
     - Regex patterns for phone numbers, UPI (`\w+@\w+`), URLs, wallet IDs
     - Scoring heuristic: base score from keyword matches + penalties/bonuses (urgency words add +0.3, phone/upi present add +0.4)
     - Return JSON: `{score: float, reasons: [strings], matches: {phones:[], upis:[], urls:[]}}`
   - Unit tests: `dev-scripts/test_detector.py` with 10 positive & negative cases.

5. Light ML classifier (optional, 4–8 hours)
   - Use scikit-learn TF‑IDF + LogisticRegression:
     - `dev-scripts/train_model.py` reads `data/labels.csv`, splits 80/20, trains, exports with `joblib`.
   - Implement `backend/app/model_runner.py` to load model at startup and provide `predict_proba(text)`.

6. FastAPI endpoints & auth (2–3 hours)
   - `/health` — simple status.
   - `POST /v1/message`:
     - Validate payload (Pydantic schema).
     - Run rule detector first; if score > 0.5 or model says suspicious, create session/message records, return `scamProbability` and `sessionId`.
     - If suspicious, include `routeToAgent: true` in response.
   - `POST /v1/admin/terminate-session` — admin-only kill switch (admin `x-api-key`).
   - Implement `x-api-key` middleware in `auth.py` reading from `.env`.

7. Persistence (1–2 hours)
   - SQLAlchemy models:
     - `Session` (id, metadata JSON, persona, created_at)
     - `Message` (id, session_id, sender, text, timestamp, raw)
     - `Extraction` (id, session_id, type, value, confidence, source, message_id)
   - Use SQLite file `data/sentinel.db` for zero-cost persistence.

8. Deliverables & verification (30–60 minutes)
   - `dev-scripts/test_ingest.py` posts sample payloads and asserts response shape.
   - README with run steps and ngrok instructions.
   - Checkpoint: manual run — `uvicorn backend.app.main:app --reload --port 8000`, POST sample message, confirm `scamProbability` returned.

Security & best practices
- Store server keys in `.env` (never in frontend).
- Rate-limit endpoints locally if possible (simple in-memory counters).

