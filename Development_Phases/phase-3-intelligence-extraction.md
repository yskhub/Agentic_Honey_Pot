# Phase 3 — Intelligence Extraction

Goal
Extract structured intelligence (phone numbers, UPI IDs, wallets, domains, scripts) reliably using deterministic extractors, spaCy, and validated JSON outputs.

Tech stack (zero cost)
- Python
- spaCy (`en_core_web_sm`)
- phonenumbers
- regex
- Pydantic + JSON Schema
- SQLite (store extractions)
- FAISS (optional for similarity/deduplication)

Prerequisites
- Phase 1 & 2 complete (ingestion + agent)
- `pip install spacy phonenumbers` and `python -m spacy download en_core_web_sm`

Step-by-step tasks (full details)

1. Define canonical extraction schema (30 minutes)
   - `schemas/intelligence_schema.json` with fields:
     - phoneNumbers: [{value, normalized, confidence, message_id}]
     - upiIds: [{value, confidence, message_id}]
     - walletIds, domains, phishingLinks, scamScripts, suspiciousKeywords
   - Create Pydantic models in `backend/app/schemas_intel.py`.

2. Implement regex extractors (2–3 hours)
   - Phone extractor using `phonenumbers`:
     - Parse candidate tokens, normalize to E.164 when possible.
   - UPI extractor:
     - Patterns: `\b[A-Za-z0-9.\-_]{2,}@[a-zA-Z]+\b`
     - Known operator list to validate (`paytm`, `upi`, `okaxis`, etc.)
   - URL extractor:
     - Robust URL regex and obfuscated patterns (e.g., "example [dot] com").

3. NER-based extraction (1–2 hours)
   - Use spaCy pipeline for PERSON/ORG/GPE tags; map ORG/person to possible social engineering targets.
   - Crosscheck with regex outputs to increase confidence.

4. LLM-based normalization fallback (optional, 1–2 hours)
   - If ambiguity persists, call local LLM wrapper to request JSON matching `intelligence_schema`.
   - Validate LLM output against Pydantic models and regex-derived values.

5. Confidence rules & deduplication (1 hour)
   - Confidence scoring:
     - regex match = 0.9
     - phonenumbers parse = 0.95
     - spaCy mention overlap = 0.6
     - LLM-sourced = 0.5–0.7
   - Deduplicate by normalizing values and hashing.

6. Storing & provenance (1 hour)
   - Save entries to `extractions` table with columns: id, session_id, message_id, type, value, normalized, confidence, source, created_at.
   - Store `provenance` JSON linking to raw message text and offsets.

7. Validation & test harness (2 hours)
   - `dev-scripts/run_extraction_demo.py` runs extractors on sample messages and writes results to `data/extraction_samples.json`.
   - Unit tests for each extractor.

Deliverables
- `backend/extractors` module, Pydantic schema, extraction DB table, demo script.

