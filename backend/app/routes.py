from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from .schemas import IngestRequest, IngestResponse
from .auth import require_api_key, require_admin_key
from .detector import detect
from .db import SessionLocal, init_db, Session as DBSess, Message as DBMessage, Extraction as DBExtraction, get_db
from sqlalchemy.orm import Session
from .audit import append_event
from datetime import datetime
from .circuit_breaker import outgoing_breaker
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
from backend.phase4.metrics import MESSAGES_TOTAL
from backend.phase4.metrics import DETECTOR_INVOCATIONS
from .sse_broker import get_broker
from fastapi import Request, HTTPException
import asyncio
from jose import jwt as jose_jwt, JWTError as JoseJWTError
from fastapi import Response
from fastapi.responses import JSONResponse
from base64 import b64decode
from typing import Tuple
from .profiler import get_recent_slow_requests

router = APIRouter()


def _sse_defaults() -> tuple:
    """Return (history_limit, max_lifetime) for SSE streams.
    - If explicit env vars `SSE_HISTORY_LIMIT` or `SSE_MAX_LIFETIME` are set, use them.
    - In CI/test environments return conservative defaults to avoid long-running tests.
    """
    try:
        # explicit env overrides
        limit = os.getenv('SSE_HISTORY_LIMIT')
        max_life = os.getenv('SSE_MAX_LIFETIME')
        if limit is not None:
            try:
                limit_val = int(limit)
            except Exception:
                limit_val = None
        else:
            limit_val = None
        if max_life is not None:
            try:
                max_life_val = int(max_life)
            except Exception:
                max_life_val = None
        else:
            max_life_val = None

        # CI/test conservative defaults when not explicitly configured
        if (os.getenv('CI') or os.getenv('GITHUB_ACTIONS') or os.getenv('PYTEST_CURRENT_TEST')) and limit_val is None and max_life_val is None:
            return (25, 2)

        return (limit_val, max_life_val)
    except Exception:
        return (None, None)
from .guvi_callback import send_guvi_callback

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/v1/message", response_model=IngestResponse)
def ingest_message(payload: IngestRequest, db: Session = Depends(get_db), authorized: bool = Depends(require_api_key), background_tasks: BackgroundTasks = None):
    # Ensure session exists
    # rate limiting per API key
    if not is_allowed(authorized):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    sess = db.query(DBSess).filter(DBSess.id == payload.sessionId).first()
    if not sess:
        sess = DBSess(id=payload.sessionId, metadata_json=json.dumps(payload.metadata or {}))
        db.add(sess)
        db.commit()
    # Merge any provided conversationHistory into DB (best-effort)
    try:
        if payload.conversationHistory:
            for m in payload.conversationHistory:
                # avoid exact-duplicate inserts by checking for same timestamp+text
                exists = db.query(DBMessage).filter(DBMessage.session_id == payload.sessionId, DBMessage.sender == m.sender, DBMessage.text == m.text, DBMessage.timestamp == m.timestamp).first()
                if not exists:
                    hist_msg = DBMessage(session_id=payload.sessionId, sender=m.sender, text=m.text, timestamp=m.timestamp, raw=m.text)
                    db.add(hist_msg)
            db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
    # store incoming message
    msg = DBMessage(session_id=payload.sessionId, sender=payload.message.sender, text=payload.message.text, timestamp=payload.message.timestamp, raw=payload.message.text)
    db.add(msg)
    db.commit()

    # publish to SSE broker so live UIs can receive updates
    try:
        broker = get_broker()
        # publish payload.message as JSON minimal
        import json as _json
        asyncio.get_event_loop().create_task(broker.publish(f'session:{payload.sessionId}', _json.dumps({'sender': payload.message.sender, 'text': payload.message.text, 'timestamp': payload.message.timestamp.isoformat() if payload.message.timestamp else None})))
    except Exception:
        pass
    try:
        MESSAGES_TOTAL.inc()
    except Exception:
        pass

    # run detector
    try:
        DETECTOR_INVOCATIONS.inc()
    except Exception:
        pass
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
                    # prefer persona set on session if available
                    persona_id = getattr(sess, 'persona', None) or None
                    resp = agent_respond(payload.sessionId, payload.message.text, db, persona_id or 'honeypot_default', background_tasks=background_tasks)
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



@router.get('/admin/ui/sessions')
def admin_ui_sessions(db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    rows = db.query(DBSess).order_by(DBSess.created_at.desc()).limit(200).all()
    out = []
    for r in rows:
        out.append({
            'id': r.id,
            'persona': r.persona,
            'created_at': r.created_at.isoformat() if r.created_at else None
        })
    return out


@router.get('/admin/ui/session/{session_id}')
def admin_ui_session(session_id: str, db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    sess = db.query(DBSess).filter(DBSess.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail='session not found')
    messages = db.query(DBMessage).filter(DBMessage.session_id == session_id).order_by(DBMessage.timestamp).all()
    extractions = db.query(DBExtraction).filter(DBExtraction.session_id == session_id).all()
    return {
        'session': {'id': sess.id, 'persona': sess.persona, 'metadata': sess.metadata_json, 'created_at': sess.created_at.isoformat() if sess.created_at else None},
        'messages': [{'id': m.id, 'sender': m.sender, 'text': m.text, 'timestamp': m.timestamp.isoformat() if m.timestamp else None} for m in messages],
        'extractions': [{'id': e.id, 'type': e.type, 'value': e.value, 'confidence': e.confidence} for e in extractions]
    }


@router.get('/admin/ui/session/{session_id}/export.csv')
def admin_ui_session_export_csv(session_id: str, db: Session = Depends(get_db), admin: bool = Depends(require_admin_key)):
    messages = db.query(DBMessage).filter(DBMessage.session_id == session_id).order_by(DBMessage.timestamp).all()
    extractions = db.query(DBExtraction).filter(DBExtraction.session_id == session_id).all()

    def iter_csv():
        header = 'type,id,sender,text,timestamp,extract_type,extract_value,extract_confidence\n'
        yield header
        for m in messages:
            # for each message, include any extraction rows (or blanks)
            related = [e for e in extractions if getattr(e, 'message_id', None) == getattr(m, 'id', None)]
            safe_text = (m.text or '').replace('"', '""')
            if not related:
                row = f'message,{m.id},{m.sender},"{safe_text}",{m.timestamp.isoformat() if m.timestamp else ""},,,\n'
                yield row
            else:
                for e in related:
                    safe_val = (e.value or '').replace('"', '""')
                    row = f'message,{m.id},{m.sender},"{safe_text}",{m.timestamp.isoformat() if m.timestamp else ""},{e.type},"{safe_val}",{e.confidence}\n'
                    yield row

    return StreamingResponse(iter_csv(), media_type='text/csv')


@router.get('/v1/session/{session_id}/result')
def session_result(session_id: str, db: Session = Depends(get_db), authorized: bool = Depends(require_api_key)):
    # Build structured intelligence and engagement metrics for a session
    messages = db.query(DBMessage).filter(DBMessage.session_id == session_id).order_by(DBMessage.timestamp).all()
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
    engagement_seconds = 0
    if total_messages >= 2:
        try:
            first = messages[0].timestamp
            last = messages[-1].timestamp
            if first and last:
                engagement_seconds = int((last - first).total_seconds())
        except Exception:
            engagement_seconds = 0

    # agent notes from conversation state
    agent_notes = None
    try:
        from .db import ConversationState
        cs = db.query(ConversationState).filter(ConversationState.session_id == session_id).first()
        if cs:
            agent_notes = cs.last_agent_reply
    except Exception:
        agent_notes = None

    scam_detected = bool(extractions) or any((m.sender == 'agent') for m in messages)

    return {
        "status": "success",
        "scamDetected": scam_detected,
        "engagementMetrics": {"engagementDurationSeconds": engagement_seconds, "totalMessagesExchanged": total_messages},
        "extractedIntelligence": extracted,
        "agentNotes": agent_notes or ""
    }


@router.get('/admin/ui/sse/session/{session_id}')
async def admin_ui_sse_session(session_id: str, request: Request, db: Session = Depends(get_db)):
    # accept either admin API key (dev) or a short-lived JWT token via `token` query param
    api_key = request.headers.get('x-api-key')
    token = request.query_params.get('token')
    expected = os.getenv('ADMIN_API_KEY')
    sse_secret = os.getenv('ADMIN_SSE_SECRET', expected or '')

    authorized = False
    if expected and api_key == expected:
        authorized = True
    if not authorized and token:
        try:
            payload = jose_jwt.decode(token, sse_secret, algorithms=['HS256'])
            # minimal validation: ensure session matches and not expired (jose validates exp)
            if payload.get('session_id') == session_id:
                authorized = True
        except JoseJWTError:
            authorized = False

    if not authorized:
        raise HTTPException(status_code=403, detail='Admin credentials required')

    # subscribe to broker channel for this session
    broker = get_broker()

    async def event_generator():
        # first, yield existing messages once (yield bytes and give control to event loop)
        # yield a limited set of historical messages (most recent first) when configured,
        # otherwise in production return full history. Defaults are environment-specific
        # and come from `_sse_defaults()` (CI/test get conservative defaults).
        limit, max_lifetime = _sse_defaults()
        if limit:
            rows = db.query(DBMessage).filter(DBMessage.session_id == session_id).order_by(DBMessage.timestamp.desc()).limit(limit).all()
        else:
            rows = db.query(DBMessage).filter(DBMessage.session_id == session_id).order_by(DBMessage.timestamp.desc()).all()
        # rows are newest-first; send them oldest-first to preserve chronology
        rows = list(reversed(rows))
        for r in rows:
            data = {'type': 'message', 'id': r.id, 'sender': r.sender, 'text': r.text, 'timestamp': r.timestamp.isoformat() if r.timestamp else None}
            chunk = (f"data: {json.dumps(data)}\n\n").encode('utf-8')
            yield chunk
            try:
                await asyncio.sleep(0)
            except Exception:
                pass

        # then stream pubsub messages
        chan = f'session:{session_id}'
        # send an initial heartbeat so clients get something immediately
        try:
            heartbeat = (": ping\n\n").encode('utf-8')
            yield heartbeat
            try:
                await asyncio.sleep(0)
            except Exception:
                pass
        except Exception:
            pass

        # proceed to streaming pubsub messages using non-blocking get_message
        start_time = asyncio.get_event_loop().time()
        try:
            while True:
                if await request.is_disconnected():
                    break
                # stop streaming after configured lifetime to avoid long-running tests
                if max_lifetime is not None and asyncio.get_event_loop().time() - start_time > max_lifetime:
                    break
                try:
                    # Prefer broker.get_message which returns None on timeout
                    msg = None
                    try:
                        msg = await broker.get_message(chan, timeout=1.0)
                    except AttributeError:
                        # older broker implementations may not have get_message
                        # fall back to a short subscribe iteration
                        async for m in broker.subscribe(chan):
                            msg = m
                            break

                    if msg is None:
                        # no message this interval; continue to check disconnect
                        continue

                    # msg may be JSON text
                    chunk = (f"data: {msg}\n\n").encode('utf-8')
                    yield chunk
                    try:
                        await asyncio.sleep(0)
                    except Exception:
                        pass
                except asyncio.CancelledError:
                    break
                except Exception:
                    # swallow errors and continue streaming
                    continue
        except asyncio.CancelledError:
            return

    return StreamingResponse(event_generator(), media_type='text/event-stream')


@router.get('/admin/ui/slow-requests')
def admin_ui_slow_requests(limit: int = 50, admin: bool = Depends(require_admin_key)):
    """Admin-only endpoint returning recent slow requests recorded by profiler."""
    items = get_recent_slow_requests(limit=limit)
    return {'count': len(items), 'items': items}


@router.post('/admin/ui/token')
def admin_ui_token(request: Request):
    # Requires admin API key in header. Returns a short-lived HS256 token for SSE use.
    api_key = request.headers.get('x-api-key')
    expected = os.getenv('ADMIN_API_KEY')
    if not expected or api_key != expected:
        raise HTTPException(status_code=403, detail='Admin credentials required')

    # Read JSON body with optional session_id and expiry seconds
    try:
        body = request.json() if hasattr(request, 'json') else None
    except Exception:
        body = None
    session_id = None
    exp_seconds = 120
    try:
        data = request._body or {}
    except Exception:
        data = None
    # use query params fallback
    params = request.query_params
    if 'session_id' in params:
        session_id = params.get('session_id')
    # construct token
    from time import time
    sse_secret = os.getenv('ADMIN_SSE_SECRET', expected)
    payload = {'iat': int(time()), 'exp': int(time()) + exp_seconds}
    if session_id:
        payload['session_id'] = session_id
    try:
        token = jose_jwt.encode(payload, sse_secret, algorithm='HS256')
        return {'token': token, 'expires_in': exp_seconds}
    except Exception as e:
        raise HTTPException(status_code=500, detail='token_generation_failed')


@router.post('/admin/ui/token-proxy')
def admin_ui_token_proxy(request: Request):
    """Issue a short-lived SSE token to authenticated judge clients.

    Authentication options:
    - `x-judge-token` header matching `JUDGE_SHARED_SECRET` env var
    - HTTP Basic auth with username `judge` and password = `JUDGE_SHARED_SECRET`
    Returns: {token, expires_in}
    """
    judge_secret = os.getenv('JUDGE_SHARED_SECRET')
    if not judge_secret:
        raise HTTPException(status_code=501, detail='Judge proxy not configured')

    # Check header
    hdr = request.headers.get('x-judge-token')
    auth_ok = False
    if hdr and hdr == judge_secret:
        auth_ok = True

    # Check basic auth
    if not auth_ok:
        auth = request.headers.get('authorization')
        if auth and auth.lower().startswith('basic '):
            try:
                creds = b64decode(auth.split(' ',1)[1]).decode('utf-8')
                user, pwd = creds.split(':',1)
                if pwd == judge_secret and user == 'judge':
                    auth_ok = True
            except Exception:
                auth_ok = False

    if not auth_ok:
        raise HTTPException(status_code=403, detail='Judge credentials required')

    params = request.query_params
    session_id = params.get('session_id')
    exp_seconds = int(os.getenv('ADMIN_SSE_TOKEN_TTL', '120'))
    from time import time
    sse_secret = os.getenv('ADMIN_SSE_SECRET', os.getenv('ADMIN_API_KEY', ''))
    payload = {'iat': int(time()), 'exp': int(time()) + exp_seconds}
    if session_id:
        payload['session_id'] = session_id
    try:
        token = jose_jwt.encode(payload, sse_secret, algorithm='HS256')
        append_event('token_issued', {'session_id': session_id})
        return {'token': token, 'expires_in': exp_seconds}
    except Exception:
        raise HTTPException(status_code=500, detail='token_generation_failed')


@router.options('/admin/ui/judge-login')
def admin_ui_judge_login_options(request: Request):
    origin = request.headers.get('origin') or '*'
    headers = {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Credentials': 'true'
    }
    return JSONResponse({'ok': True}, headers=headers)


@router.post('/admin/ui/judge-login')
def admin_ui_judge_login(request: Request, body: dict = None):
    """Authenticate a judge username/password and return a short-lived SSE token.

    Configure judge users via env `JUDGE_USERS` as `user1:pass1,user2:pass2`.
    This endpoint returns `{token, expires_in}` on success.
    """
    users_env = os.getenv('JUDGE_USERS', '')
    # Debug: log incoming headers and body to help diagnose CORS/fetch issues
    try:
        hdrs = {k: v for k, v in request.headers.items() if k.lower() in ('origin','content-type','referer')}
        print('DEBUG judge_login headers:', hdrs)
        print('DEBUG judge_login body:', body)
    except Exception:
        pass
    users = {}
    for pair in [p for p in users_env.split(',') if p.strip()]:
        if ':' in pair:
            u, p = pair.split(':', 1)
            users[u] = p

    if not body:
        raise HTTPException(status_code=400, detail='username/password required')
    username = body.get('username')
    password = body.get('password')
    session_id = body.get('session_id')
    if not username or not password:
        raise HTTPException(status_code=400, detail='username/password required')
    if username not in users or users.get(username) != password:
        raise HTTPException(status_code=403, detail='invalid credentials')

    # issue token
    from time import time
    exp_seconds = int(os.getenv('ADMIN_SSE_TOKEN_TTL', '120'))
    sse_secret = os.getenv('ADMIN_SSE_SECRET', os.getenv('ADMIN_API_KEY', ''))
    payload = {'iat': int(time()), 'exp': int(time()) + exp_seconds, 'judge': username}
    if session_id:
        payload['session_id'] = session_id
    try:
        token = jose_jwt.encode(payload, sse_secret, algorithm='HS256')
        append_event('judge_login', {'judge': username, 'session_id': session_id})
        origin = request.headers.get('origin') or ''
        headers = {'Access-Control-Allow-Origin': origin or '*', 'Access-Control-Allow-Credentials': 'true'}
        return JSONResponse({'token': token, 'expires_in': exp_seconds}, headers=headers)
    except Exception:
        raise HTTPException(status_code=500, detail='token_generation_failed')


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
