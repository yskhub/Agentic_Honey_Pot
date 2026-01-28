from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from .schemas import IngestRequest, IngestResponse
from .auth import require_api_key, require_admin_key
from .detector import detect
from .db import SessionLocal, init_db, Session as DBSess, Message as DBMessage, Extraction as DBExtraction, get_db
from sqlalchemy.orm import Session
from .audit import append_event
from datetime import datetime
import os
from .rate_limit import is_allowed, get_usage
from .callback_queue import enqueue
import json
import requests
from .agent import respond as agent_respond
from .db import OutgoingMessage as DBOutgoing
from typing import Optional
from fastapi.responses import StreamingResponse
import csv
from io import StringIO

router = APIRouter()

def send_guvi_callback(payload: dict):
    guvi_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    guvi_key = os.getenv("GUVI_API_KEY", "")
    headers = {"Content-Type": "application/json", "x-api-key": guvi_key}
    # simple retry loop
    attempts = 0
    max_attempts = 3
    backoff = 1
    while attempts < max_attempts:
        try:
            resp = requests.post(guvi_url, json=payload, headers=headers, timeout=5)
            resp.raise_for_status()
            append_event("guvi_callback_sent", {"payload": payload, "status": resp.status_code})
            return {"status": "sent", "code": resp.status_code}
        except Exception as e:
            attempts += 1
            append_event("guvi_callback_error", {"attempt": attempts, "error": str(e)})
            import time
            time.sleep(backoff)
            backoff *= 2
    # enqueue for persistent retry
    try:
        enqueue(payload)
    except Exception:
        append_event("enqueue_failed", {"sessionId": payload.get("sessionId")})
    return {"status": "failed_enqueued", "attempts": attempts}

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/v1/message", response_model=IngestResponse)
def ingest_message(payload: IngestRequest, db: Session = Depends(get_db), authorized: bool = Depends(require_api_key)):
    # Ensure session exists
    # rate limiting per API key
    if not is_allowed(authorized):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    sess = db.query(DBSess).filter(DBSess.id == payload.sessionId).first()
    if not sess:
        sess = DBSess(id=payload.sessionId, metadata_json=json.dumps(payload.metadata or {}))
        db.add(sess)
        db.commit()
    # store incoming message
    msg = DBMessage(session_id=payload.sessionId, sender=payload.message.sender, text=payload.message.text, timestamp=payload.message.timestamp, raw=payload.message.text)
    db.add(msg)
    db.commit()

    # run detector
    det = detect(payload.message.text)
    score = det["score"]
    route = score >= float(os.getenv("DETECTOR_THRESHOLD", 0.5))

    # save extractions (simple)
    for p in det["matches"].get("phones", []):
        ex = DBExtraction(session_id=payload.sessionId, type="phone", value=p, confidence=0.9)
        db.add(ex)
    for u in det["matches"].get("upis", []):
        ex = DBExtraction(session_id=payload.sessionId, type="upi", value=u, confidence=0.9)
        db.add(ex)
    for u in det["matches"].get("urls", []):
        ex = DBExtraction(session_id=payload.sessionId, type="url", value=u, confidence=0.8)
        db.add(ex)
    db.commit()

    # audit event
    try:
        append_event("ingest_message", {"sessionId": payload.sessionId, "score": score, "reasons": det.get("reasons", [])})
    except Exception:
        pass

    agent_reply = None
    if route:
        # check human override
        try:
            from .db import ConversationState
            cs = db.query(ConversationState).filter(ConversationState.session_id == payload.sessionId).first()
            if cs and cs.human_override:
                append_event('agent_skipped_human_override', {'sessionId': payload.sessionId})
            else:
                # auto-respond using agent and persist agent message
                try:
                    resp = agent_respond(payload.sessionId, payload.message.text, db)
                    agent_reply = resp.get('reply')
                    append_event('agent_auto_reply', {'sessionId': payload.sessionId, 'reply': agent_reply})
                except Exception:
                    pass
        except Exception:
            pass

    return IngestResponse(scamProbability=score, routeToAgent=route, sessionId=payload.sessionId, reasons=det["reasons"]) if not agent_reply else {"scamProbability": score, "routeToAgent": route, "sessionId": payload.sessionId, "reasons": det["reasons"], "agentReply": agent_reply}


@router.post("/v1/admin/override-session")
def override_session(data: dict, db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    session_id = data.get('sessionId')
    enable = data.get('enable', True)
    if not session_id:
        raise HTTPException(status_code=400, detail="sessionId required")
    from .db import ConversationState
    cs = db.query(ConversationState).filter(ConversationState.session_id == session_id).first()
    if not cs:
        cs = ConversationState(session_id=session_id, human_override=bool(enable))
        db.add(cs)
    else:
        cs.human_override = bool(enable)
    db.commit()
    append_event('override_set', {'sessionId': session_id, 'enabled': bool(enable)})
    return {'status': 'ok', 'sessionId': session_id, 'human_override': bool(enable)}

@router.post("/v1/admin/terminate-session")
def terminate_session(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    session_id = data.get("sessionId")
    if not session_id:
        raise HTTPException(status_code=400, detail="sessionId required")
    # Build payload from DB
    messages = db.query(DBMessage).filter(DBMessage.session_id == session_id).all()
    extractions = db.query(DBExtraction).filter(DBExtraction.session_id == session_id).all()
    extracted = {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "suspiciousKeywords": []}
    for e in extractions:
        if e.type == "phone":
            extracted["phoneNumbers"].append(e.value)
        if e.type == "upi":
            extracted["upiIds"].append(e.value)
        if e.type == "url":
            extracted["phishingLinks"].append(e.value)
    total_messages = len(messages)
    guvi_payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": extracted,
        "agentNotes": "Auto-terminated by admin"
    }
    # schedule background callback with retries
    background_tasks.add_task(send_guvi_callback, guvi_payload)
    append_event("terminate_scheduled", {"sessionId": session_id, "messages": total_messages})
    return {"status": "scheduled"}


@router.post("/v1/agent/message")
def agent_message(data: dict, db: Session = Depends(get_db), authorized: bool = Depends(require_api_key)):
    session_id = data.get('sessionId')
    text = data.get('text')
    if not session_id or not text:
        raise HTTPException(status_code=400, detail="sessionId and text required")
    # simple agent response
    resp = agent_respond(session_id, text)
    append_event('agent_reply', {'sessionId': session_id, 'text': text, 'reply': resp.get('reply')})
    return resp


@router.get('/v1/admin/outgoing')
def list_outgoing(status: Optional[str] = None, q: Optional[str] = None, page: int = 1, page_size: int = 50, db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    qdb = db.query(DBOutgoing)
    if status:
        qdb = qdb.filter(DBOutgoing.status == status)
    if q:
        like = f"%{q}%"
        qdb = qdb.filter(DBOutgoing.content.ilike(like) | DBOutgoing.session_id.ilike(like))
    total = qdb.count()
    page = max(1, page)
    offset = (page - 1) * page_size
    rows = qdb.order_by(DBOutgoing.created_at.desc()).offset(offset).limit(page_size).all()
    res = {'total': total, 'page': page, 'page_size': page_size, 'items': []}
    for r in rows:
        res['items'].append({'id': r.id, 'sessionId': r.session_id, 'content': r.content, 'status': r.status, 'created_at': r.created_at.isoformat() if r.created_at else None})
    return res


@router.post('/v1/admin/outgoing/{msg_id}/retry')
def retry_outgoing(msg_id: int, db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    row = db.query(DBOutgoing).filter(DBOutgoing.id == msg_id).first()
    if not row:
        raise HTTPException(status_code=404, detail='not found')
    row.status = 'queued'
    db.add(row)
    db.commit()
    append_event('outgoing_retry', {'id': msg_id})
    return {'status': 'queued', 'id': msg_id}


@router.delete('/v1/admin/outgoing/{msg_id}')
def delete_outgoing(msg_id: int, db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    row = db.query(DBOutgoing).filter(DBOutgoing.id == msg_id).first()
    if not row:
        raise HTTPException(status_code=404, detail='not found')
    db.delete(row)
    db.commit()
    append_event('outgoing_deleted', {'id': msg_id})
    return {'status': 'deleted', 'id': msg_id}


@router.get('/admin/ui/outgoing')
def admin_outgoing_ui():
        # Serve a small SPA that requests an admin token at runtime (never embeds secrets)
        html = '''
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Outgoing Messages</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                #controls { margin-bottom: 12px; }
                .card { border: 1px solid #e0e0e0; padding: 8px; margin: 6px 0; border-radius: 4px; }
                button { margin-right: 6px; }
                pre { background:#fafafa; padding:8px; overflow:auto }
            </style>
        </head>
        <body>
        <h3>Outgoing Messages — Admin</h3>
        <div id="login">
            <label>Admin token: <input id="token" type="password" style="width:300px" /></label>
            <button id="loginBtn">Use token</button>
        </div>
        <div id="app" style="display:none">
            <div id="controls">
                <input id="q" placeholder="search session or content" style="width:40%" />
                <select id="status"><option value="">any</option><option value="queued">queued</option><option value="sent">sent</option><option value="failed">failed</option></select>
                <button id="search">Search</button>
                <button id="export">Export CSV</button>
            </div>
            <div id="list">Loading...</div>
            <div id="pager"></div>
        </div>
        <script>
            let ADMIN_TOKEN = null;
            function authHeaders(){
                if(!ADMIN_TOKEN) return {};
                return { 'Authorization': 'Bearer ' + ADMIN_TOKEN };
            }
            document.getElementById('loginBtn').onclick = ()=>{
                ADMIN_TOKEN = document.getElementById('token').value.trim();
                if(!ADMIN_TOKEN){ alert('Enter token'); return }
                document.getElementById('login').style.display='none';
                document.getElementById('app').style.display='block';
                load();
            }
            async function load(page=1){
                const q = document.getElementById('q').value;
                const status = document.getElementById('status').value;
                const url = new URL('/v1/admin/outgoing', location.origin);
                if(q) url.searchParams.append('q', q);
                if(status) url.searchParams.append('status', status);
                url.searchParams.append('page', page);
                url.searchParams.append('page_size', 20);
                const res = await fetch(url.toString(), {headers: authHeaders()})
                if(res.status === 403){ alert('Unauthorized: invalid admin token'); return }
                const data = await res.json();
                const el = document.getElementById('list');
                el.innerHTML = '';
                data.items.forEach(item=>{
                        const d = document.createElement('div'); d.className='card';
                        d.innerHTML = `<b>id</b>: ${item.id} <b>session</b>: ${item.sessionId} <br><b>status</b>: ${item.status} <br><pre>${item.content}</pre>`;
                        const retry = document.createElement('button'); retry.textContent='Retry'; retry.onclick=()=>fetch(`/v1/admin/outgoing/${item.id}/retry`,{method:'POST',headers:authHeaders()}).then(()=>load(page));
                        const del = document.createElement('button'); del.textContent='Delete'; del.onclick=()=>{ if(confirm('Delete message '+item.id+'?')) fetch(`/v1/admin/outgoing/${item.id}`,{method:'DELETE',headers:authHeaders()}).then(()=>load(page)); };
                        d.appendChild(retry); d.appendChild(del);
                        el.appendChild(d);
                })
                const pager = document.getElementById('pager');
                pager.innerHTML = `Page ${data.page} / ${Math.max(1, Math.ceil(data.total / data.page_size || 1))}`;
            }
            document.getElementById('search').onclick = ()=>load(1);
            document.getElementById('export').onclick = async ()=>{
                const q = document.getElementById('q').value;
                const status = document.getElementById('status').value;
                const url = new URL('/v1/admin/outgoing.csv', location.origin);
                if(q) url.searchParams.append('q', q);
                if(status) url.searchParams.append('status', status);
                url.searchParams.append('page_size', 1000);
                url.searchParams.append('page', 1);
                const res = await fetch(url.toString(), {headers: authHeaders()});
                if(res.status === 403){ alert('Unauthorized: invalid admin token'); return }
                const blob = await res.blob();
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = 'outgoing.csv';
                link.click();
            }
        </script>
        </body>
        </html>
        '''
        return HTMLResponse(html)


@router.get('/v1/admin/outgoing.csv')
def export_outgoing(status: Optional[str] = None, q: Optional[str] = None, page: int = 1, page_size: int = 1000, db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    qdb = db.query(DBOutgoing)
    if status:
        qdb = qdb.filter(DBOutgoing.status == status)
    if q:
        like = f"%{q}%"
        qdb = qdb.filter(DBOutgoing.content.ilike(like) | DBOutgoing.session_id.ilike(like))
    offset = (max(1, page) - 1) * page_size
    rows = qdb.order_by(DBOutgoing.created_at.desc()).offset(offset).limit(page_size).all()

    def iter_csv():
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['id', 'sessionId', 'status', 'created_at', 'content'])
        yield si.getvalue()
        si.seek(0); si.truncate(0)
        for r in rows:
            writer.writerow([r.id, r.session_id, r.status, r.created_at.isoformat() if r.created_at else '', r.content])
            yield si.getvalue()
            si.seek(0); si.truncate(0)

    return StreamingResponse(iter_csv(), media_type='text/csv')
