import json
import random
import os
from typing import Dict, Optional
from datetime import datetime
import json
import re

from .db import Message as DBMessage, ConversationState as CSModel, OutgoingMessage as OutMsg, Extraction as DBExtraction
from .audit import append_event
from backend.safety.safety_rules import check_reply_safety
from .guvi_callback import send_guvi_callback
import threading

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


def respond(session_id: str, incoming_text: str, db: Optional[object] = None, persona_id: str = 'honeypot_default', background_tasks: Optional[object] = None) -> Dict:
    persona = load_persona(persona_id)
    reply, slots = simple_match(incoming_text, persona)

    # Run safety checks on the generated reply. If the reply is unsafe,
    # replace with a safe fallback or a redacted version.
    try:
        safe_res = check_reply_safety(reply)
        if not safe_res.get('allowed', True):
            append_event('safety_blocked_reply', {'sessionId': session_id, 'reason': safe_res.get('reason'), 'original': reply})
            reply = safe_res.get('sanitized') or "I'm unable to assist with that request."
        else:
            # if redacted, use sanitized text
            if safe_res.get('reason') == 'redacted_digits' and safe_res.get('sanitized'):
                reply = safe_res.get('sanitized')
    except Exception:
        # On safety subsystem failures, prefer to be conservative and leave reply unchanged
        try:
            append_event('safety_check_error', {'sessionId': session_id})
        except Exception:
            pass

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
        # Check for conversation completion and trigger final GUVI callback asynchronously
        try:
            # completion rules: persona setting -> env override -> defaults
            persona_complete_after = persona.get('complete_after_turns')
            env_complete_after = os.getenv('AGENT_COMPLETE_AFTER_TURNS')
            try:
                if env_complete_after is not None:
                    complete_after = int(env_complete_after)
                elif persona_complete_after is not None:
                    complete_after = int(persona_complete_after)
                else:
                    complete_after = 6
            except Exception:
                complete_after = 6

            # slot-based completion: persona may define required completion_slots list
            completion_slots = persona.get('completion_slots', []) if isinstance(persona.get('completion_slots', []), list) else []

            # phrase-based completion detection on incoming text
            end_phrases = ['thank you', 'thanks', 'bye', 'ok done', 'done', 'goodbye']

            # reload conversation state
            cs = db.query(CSModel).filter(CSModel.session_id == session_id).first()
            is_complete = False
            if cs and (cs.turn_count or 0) >= int(complete_after):
                is_complete = True

            # check completion slots
            if completion_slots and cs:
                try:
                    slots = json.loads(cs.slots_json) if cs.slots_json else {}
                    if all(s in slots and slots.get(s) for s in completion_slots):
                        is_complete = True
                except Exception:
                    pass

            # phrase check on last incoming_text
            if incoming_text:
                tlow = (incoming_text or '').lower()
                for p in end_phrases:
                    if p in tlow:
                        is_complete = True
                        break

            if is_complete and cs:
                # build final payload
                messages = db.query(DBMessage).filter(DBMessage.session_id == session_id).order_by(DBMessage.timestamp).all()
                extractions = db.query(DBExtraction).filter(DBExtraction.session_id == session_id).all()
                extracted = {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "suspiciousKeywords": []}
                for e in extractions:
                    if e.type == 'phone':
                        extracted['phoneNumbers'].append(e.value)
                    if e.type == 'upi':
                        extracted['upiIds'].append(e.value)
                    if e.type == 'url':
                        extracted['phishingLinks'].append(e.value)
                total_messages = len(messages)
                agent_notes = cs.last_agent_reply if getattr(cs, 'last_agent_reply', None) else f"Agent completed after {cs.turn_count} turns"
                payload = {
                    'sessionId': session_id,
                    'scamDetected': True,
                    'totalMessagesExchanged': total_messages,
                    'extractedIntelligence': extracted,
                    'agentNotes': agent_notes
                }
                # schedule using BackgroundTasks when provided; otherwise fall back to thread
                try:
                    if background_tasks is not None:
                        background_tasks.add_task(send_guvi_callback, payload)
                    else:
                        t = threading.Thread(target=send_guvi_callback, args=(payload,), daemon=True)
                        t.start()
                    append_event('guvi_callback_scheduled_by_agent', {'sessionId': session_id, 'via': 'background_tasks' if background_tasks is not None else 'thread'})
                except Exception:
                    append_event('guvi_callback_schedule_failed', {'sessionId': session_id})
        except Exception:
            try:
                append_event('agent_completion_check_error', {'sessionId': session_id})
            except Exception:
                pass
    return {
        'sessionId': session_id,
        'reply': reply,
        'persona': persona.get('name')
    }
