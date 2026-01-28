# Zero-Cost Rules & Constraints

Purpose
Document constraints and operational rules to keep the entire project free of monetary cost.

Rules and guidance
- No paid APIs in judge path. Local LLMs only if run on developer hardware.
- No paid cloud infra. Use local SQLite and local files. Frontend to Vercel free if needed.
- Use OSS-compatible models and cite licenses in `data/sources.json`.
- Never put secret keys in frontend. Server-side GUVI callback must use server env key.
- Provide deterministic scripted fallbacks for all agent behaviors.

Operational checklist
- `README.md` with run commands and ngrok instructions.
- `dev-scripts/judge_simulator.py` to validate callback behavior.
- `LICENSES.md` with third-party attributions.

