import os
import json
import sqlite3
import time
from pathlib import Path
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

DB_PATH = os.getenv('SENTINEL_DB', 'data/sentinel.db')


@st.cache_resource
def get_connection(db_path: str):
    p = Path(db_path)
    if not p.exists():
        return None
    conn = sqlite3.connect(str(p), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def load_sessions(conn):
    q = "SELECT id, persona, created_at FROM sessions ORDER BY created_at DESC"
    return pd.read_sql_query(q, conn) if conn else pd.DataFrame()


def load_messages(conn, session_id):
    q = "SELECT id, sender, text, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp"
    return pd.read_sql_query(q, conn, params=(session_id,)) if conn else pd.DataFrame()


def load_extractions(conn, session_id):
    q = "SELECT id, type, value, confidence FROM extractions WHERE session_id = ?"
    return pd.read_sql_query(q, conn, params=(session_id,)) if conn else pd.DataFrame()


def export_session(conn, session_id):
    sess_q = "SELECT id, metadata FROM sessions WHERE id = ?"
    sess = conn.execute(sess_q, (session_id,)).fetchone()
    messages = [dict(r) for r in conn.execute("SELECT sender, text, timestamp, raw FROM messages WHERE session_id = ? ORDER BY timestamp", (session_id,)).fetchall()]
    extractions = [dict(r) for r in conn.execute("SELECT type, value, confidence FROM extractions WHERE session_id = ?", (session_id,)).fetchall()]
    return json.dumps({"session": dict(sess) if sess else {}, "messages": messages, "extractions": extractions}, indent=2, default=str)


def main():
    st.set_page_config(page_title="Sentinel Dashboard", layout="wide")
    st.title("Sentinel — Sessions & Extractions")

    conn = get_connection(DB_PATH)
    if not conn:
        st.error(f"Database not found at {DB_PATH}. Start backend or set SENTINEL_DB env var.")
        return
    sessions = load_sessions(conn)
    cols = st.columns([3, 1])
    with cols[0]:
        st.subheader("Sessions")
        if sessions.empty:
            st.info("No sessions found in DB.")
        else:
            selected = st.selectbox("Pick session", sessions['id'].tolist())
            st.dataframe(sessions.set_index('id'))
    with cols[1]:
        st.subheader("Controls")
        api_url = st.text_input("Backend URL (for admin ops)", value=os.getenv('BACKEND_URL', 'http://127.0.0.1:8030'))
        admin_token = st.text_input("Admin token (x-api-key)", type='password')
        # Live polling controls
        live = st.checkbox("Live (poll)", value=False)
        interval = st.number_input("Poll interval (sec)", min_value=1, max_value=60, value=5)

    if sessions.empty:
        return

    session_id = selected
    st.markdown(f"### Session: `{session_id}`")

    # If live polling is enabled, repeatedly render then sleep and rerun the script
    if 'live_mode' not in st.session_state:
        st.session_state.live_mode = False
    if live:
        st.session_state.live_mode = True
    else:
        st.session_state.live_mode = False

    msgs = load_messages(conn, session_id)
    exs = load_extractions(conn, session_id)

    st.subheader("Messages")
    if msgs.empty:
        st.write("No messages stored for this session.")
    else:
        st.table(msgs)

    st.subheader("Extractions")
    if exs.empty:
        st.write("No extractions for this session.")
    else:
        st.table(exs)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Export session JSON", data=export_session(conn, session_id), file_name=f"session_{session_id}.json", mime='application/json')
    with col2:
        if st.button("Terminate session (admin)"):
            if not admin_token:
                st.warning("Provide admin token to call backend terminate endpoint.")
            else:
                try:
                    import requests
                    r = requests.post(f"{api_url}/v1/admin/terminate-session", json={"sessionId": session_id}, headers={"x-api-key": admin_token}, timeout=5)
                    if r.status_code == 200:
                        st.success("Terminate scheduled via backend")
                    else:
                        st.error(f"Backend responded: {r.status_code} {r.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

    st.markdown("---")
    st.caption(f"Connected DB: {DB_PATH}")

    # If live polling was requested, use SSE in-browser when possible, otherwise fallback to server-side poll
    if st.session_state.get('live_mode'):
        if admin_token:
            # Obtain a short-lived token from backend using the admin token (server-side) then use it in EventSource
            try:
                import requests as _req
                token_resp = _req.post(f"{api_url}/admin/ui/token?session_id={session_id}", headers={"x-api-key": admin_token}, timeout=5)
                if token_resp.status_code == 200:
                    token = token_resp.json().get('token')
                    sse_url = f"{api_url}/admin/ui/sse/session/{session_id}?token={token}"
                    html = f"""
                    <div id="sse_status" style="font-size:12px;color:#666">Live updates enabled via SSE (token)</div>
                    <script>
                    const es = new EventSource("{sse_url}");
                    es.onmessage = function(e) {{ try {{ window.location.reload(); }} catch(err) {{ console.error(err); }} }};
                    es.onerror = function(ev) {{ document.getElementById('sse_status').innerText = 'SSE disconnected'; es.close(); }};
                    </script>
                    """
                    components.html(html, height=60)
                    time.sleep(max(1, int(interval)))
                    st.experimental_rerun()
                else:
                    st.warning('Failed to obtain SSE token; falling back to polling')
                    time.sleep(max(1, int(interval)))
                    st.experimental_rerun()
            except Exception as e:
                st.error(f'Failed to request SSE token: {e} — falling back to polling')
                time.sleep(max(1, int(interval)))
                st.experimental_rerun()
        else:
            # fallback server-side polling when SSE not available
            time.sleep(max(1, int(interval)))
            st.experimental_rerun()


if __name__ == '__main__':
    main()
