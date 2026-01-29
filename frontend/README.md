# Sentinel Dashboard (Streamlit)

Run the lightweight Streamlit dashboard to inspect sessions, messages, and extractions directly from the local SQLite DB.

Install dependencies (in your venv):

```powershell
pip install -r requirements.txt
```

Run the dashboard:

```powershell
streamlit run frontend/streamlit_app.py
```

Notes:
- By default the dashboard reads the DB at `data/sentinel.db`. Override with `SENTINEL_DB` env var.
- To trigger `terminate-session` via the backend, provide `BACKEND_URL` and an admin token in the Controls panel.
