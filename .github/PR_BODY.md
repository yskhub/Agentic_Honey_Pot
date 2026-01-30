Fix SSE test hangs — limit history & lifetime, non-blocking broker, remove test shims

Summary
- Prevents long-running SSE streams from hanging tests or local runs by:
  - limiting historical messages returned
  - limiting SSE stream lifetime by default
  - using non-blocking broker APIs for pub/sub
- Removes earlier TestClient-specific shims and adds small dev helpers.
- Keeps changes configurable via environment variables for production adjustments.

What I changed
- Behavior: SSE now returns only recent history and yields a short heartbeat before streaming live messages; streaming loop uses a non-blocking `get_message()` with a short timeout and a configurable max lifetime.
- Broker: added `get_message(channel, timeout)` and made `subscribe()` non-blocking in `MemoryBroker` and `RedisBroker`.
- Tests: adjusted `tests/test_judge_login_sse.py` to handle the runtime-safe SSE behavior (no unsupported `timeout` kwarg).
- Dev tools: added `dev-scripts/clear_test_messages.py` and `dev-scripts/debug_sse_client.py` to help reproduce and debug SSE locally.
- Removed: TestClient/requests compatibility shim and temporary early-return behavior introduced during debugging.

Files of interest
- backend/app/routes.py
- backend/app/sse_broker.py
- tests/test_judge_login_sse.py
- dev-scripts/clear_test_messages.py
- dev-scripts/debug_sse_client.py

Configuration
- New env vars:
  - `SSE_HISTORY_LIMIT` (default: `5`) — how many recent messages to include
  - `SSE_MAX_LIFETIME` (default: `2.0`) — seconds to keep an SSE connection alive in test/dev by default

Testing
- Ran full test suite locally: `python -m pytest -q` → all tests pass (17 passed, warnings).

Risk & Migration
- Low risk: defaults are conservative and configurable.
- Production operators should set `SSE_HISTORY_LIMIT` and `SSE_MAX_LIFETIME` appropriately (or unset to allow long-lived streams).

Follow-ups
- (Optional) Replace simple `SSE_MAX_LIFETIME` defaulting strategy with environment-specific defaults (CI vs prod).
- (Optional) Add integration test for live SSE under a Redis-backed broker.

Branch: `phase6/streamlit-deploy`

Please review and merge when ready.
