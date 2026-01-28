from backend.app.agent import respond
from backend.app.db import SessionLocal
from backend.app.db import Session as DBSessionModel, Message as DBMessage


def test_agent_persists_message():
    db = SessionLocal()
    sid = 'agent-test-session'
    # ensure session exists
    s = db.query(DBSessionModel).filter(DBSessionModel.id == sid).first()
    if not s:
        s = DBSessionModel(id=sid, metadata_json='{}')
        db.add(s)
        db.commit()

    # call agent respond with db
    r = respond(sid, 'Please share your UPI ID', db=db)
    assert 'reply' in r
    # check message persisted
    msg = db.query(DBMessage).filter(DBMessage.session_id == sid, DBMessage.sender == 'agent').order_by(DBMessage.id.desc()).first()
    assert msg is not None
    db.close()
