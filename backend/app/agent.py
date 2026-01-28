import json
import random
import os
from typing import Dict, Optional
from datetime import datetime
import json
import re

from .db import Message as DBMessage, ConversationState as CSModel, OutgoingMessage as OutMsg

PERSONA_DIR = os.path.join(os.path.dirname(__file__), 'personas')


def load_persona(persona_id: str = 'honeypot_default') -> Dict:
    path = os.path.join(PERSONA_DIR, 'honeypot_persona.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def simple_match(text: str, persona: Dict) -> (str, Dict):
    t = text
    # check behaviors: exact tokens, then regex
    for b in persona.get('behaviors', []):
        # token matches
        for m in b.get('match', []):
            if m.lower() in t.lower():
                return random.choice(b.get('response_templates', [])), {}
        # regex patterns
        for pattern in b.get('patterns', []) if b.get('patterns') else []:
            mobj = re.search(pattern, t, flags=re.IGNORECASE)
            if mobj:
                slots = {k: v for k, v in mobj.groupdict().items() if v is not None}
                return random.choice(b.get('response_templates', [])), slots

    # default heuristics
    digits = ''.join([c for c in t if c.isdigit()])
    if len(digits) >= 6:
        return random.choice(["Thanks — can you confirm the last 4 digits?", "Got it. What's the account holder name?"]), {}
    fallbacks = persona.get('fallbacks', [])
    if fallbacks:
        return random.choice(fallbacks), {}
    return "Okay.", {}


def respond(session_id: str, incoming_text: str, db: Optional[object] = None, persona_id: str = 'honeypot_default') -> Dict:
    persona = load_persona(persona_id)
    reply, slots = simple_match(incoming_text, persona)

    # persist agent message and queue outgoing send if db provided
    if db is not None:
        # persist agent message first (critical)
        try:
            msg = DBMessage(session_id=session_id, sender='agent', text=reply, timestamp=datetime.utcnow(), raw=reply)
            db.add(msg)
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

        # update conversation state (best-effort)
        try:
            cs = db.query(CSModel).filter(CSModel.session_id == session_id).first()
            if not cs:
                cs = CSModel(
                    session_id=session_id,
                    turn_count=1,
                    last_agent_reply=reply,
                    messages_json=json.dumps([{'sender': 'agent', 'text': reply, 'ts': datetime.utcnow().isoformat()}]),
                    slots_json=json.dumps(slots)
                )
                db.add(cs)
                db.commit()
            else:
                cs.turn_count = (cs.turn_count or 0) + 1
                cs.last_agent_reply = reply
                try:
                    msgs = json.loads(cs.messages_json) if cs.messages_json else []
                except Exception:
                    msgs = []
                msgs.append({'sender': 'agent', 'text': reply, 'ts': datetime.utcnow().isoformat()})
                cs.messages_json = json.dumps(msgs[-10:])
                try:
                    existing_slots = json.loads(cs.slots_json) if cs.slots_json else {}
                except Exception:
                    existing_slots = {}
                existing_slots.update(slots or {})
                cs.slots_json = json.dumps(existing_slots)
                db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

        # enqueue outgoing message (best-effort)
        try:
            with db.begin():
                out = OutMsg(session_id=session_id, content=reply, status='queued', created_at=datetime.utcnow())
                db.add(out)
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

    return {
        'sessionId': session_id,
        'reply': reply,
        'persona': persona.get('name')
    }
