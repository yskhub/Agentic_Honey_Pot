# Optimization & Profiling Plan (initial)

Summary
Measured a quick latency baseline for `POST /v1/message` using `dev-scripts/profile_perf.py` against a local server: mean ~5ms, max ~12ms (local dev machine).

Goals
- Keep `/v1/message` median latency < 100ms under judge demo loads.
- Ensure agent decision latency stays low (scripted replies < 100ms, LLM fallbacks properly rate-limited).
- Ensure DB writes do not block request handling.

Immediate recommendations
- Cache loaded models/vectorizers and detectors in module-global variables (already done).
- Use FastAPI BackgroundTasks or a worker to persist non-critical telemetry (audit logs) asynchronously.
- Batch or offload heavy extraction normalization tasks to worker processes (e.g., normalize phone numbers in background and attach to session record).
- Ensure the GUVI callback is performed asynchronously (already scheduled via BackgroundTasks / thread). Keep timeout short and fallback to queue on failure.

Profiling steps (next)
1. Run `dev-scripts/profile_perf.py <backend_url>` under three conditions:
   - Idle (single client)
   - 10 concurrent clients (use `xargs -P` or a small multiprocessing runner)
   - 50 concurrent clients (simulate judge load)
2. Capture CPU/memory and identify hotspots via `pyinstrument` or `cProfile`.
3. If DB I/O is hotspot, switch to async DB calls or queue writes to worker.

Optimization plan
- Short-term (low effort): Ensure background persistence of logs & callbacks; memoize expensive computations; add timeouts for external calls.
- Mid-term: Add lightweight in-memory cache for recent session state (LRU) to avoid repeated DB reads during multi-turn sessions.
- Longer-term: Containerize and run a small load test (Locust) in CI; consider using a dedicated worker process with Redis queue for outgoing callbacks & extractors.

If you want, I can implement the BackgroundTasks audit persistence change, add a simple concurrency test harness, or wire `pyinstrument` runs and collect traces.
