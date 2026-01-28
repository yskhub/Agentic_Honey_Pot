# Phase 6 — Optimization & Scale

Goal
Prepare the system for reliable judge evaluation, optimize latency, and containerize for consistent runs.

Tech stack (zero cost)
- Docker (local)
- GitHub Actions (free for public repos)
- Locust or simple scripts for load testing
- Model quantization docs if local LLMs used

Step-by-step tasks (full details)

1. Profiling & metrics (2–4 hours)
   - Add lightweight metrics and profiling:
     - Response time for `/v1/message`
     - Agent decision latency
     - DB write latency
   - Use `pyinstrument` or simple timing wrappers.

2. Caching & optimization (2–4 hours)
   - Cache loaded models/vectorizers in memory.
   - Use in-memory caches for recent sessions and recent extraction results.
   - Limit LLM calls; prefer scripted replies to maintain low latency.

3. Containerization (2–4 hours)
   - Add `Dockerfile` for backend:
     - Use slim Python base
     - Copy requirements, install, add entrypoint to run uvicorn
   - Add `docker-compose.yml` optional with Redis (if used).
   - Provide `Makefile` or script to `docker build` and `docker run`.

4. CI & smoke tests (2–4 hours)
   - GitHub Actions workflow:
     - Linting, unit tests, and a smoke test that calls `/v1/message` and `/v1/finalize` with sample payload.
   - Add badge to README.

5. Demo resilience (2 hours)
   - Pre-recorded demo scenarios as short videos or terminal recordings.
   - Provide a `demo_checklist.md` for last-minute checks:
     - Start backend, start frontend, start ngrok, ensure GUVI callback key present.

6. Quantization & local LLM (optional)
   - Document steps to quantize models for `llama.cpp` or gpt4all (links and commands).
   - Keep scripts to load quantized model if developer chooses to use local LLM.

Deliverables
- Docker artifacts, CI workflows, smoke tests, demo runbook.

