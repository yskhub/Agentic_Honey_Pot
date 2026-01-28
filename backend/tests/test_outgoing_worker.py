from backend.app.outgoing_worker import _process_one
from backend.app.db import SessionLocal, OutgoingMessage


def test_outgoing_process_one():
    db = SessionLocal()
    try:
        # create queued message
        om = OutgoingMessage(session_id='test123', content='hello', status='queued')
        db.add(om)
        db.commit()

        # process once
        _process_one(db)

        # refresh
        msg = db.query(OutgoingMessage).filter(OutgoingMessage.session_id == 'test123').first()
        assert msg is not None
        assert msg.status in ('sent', 'failed')
    finally:
        try:
            # cleanup
            db.query(OutgoingMessage).filter(OutgoingMessage.session_id == 'test123').delete()
            db.commit()
        except Exception:
            pass
        try:
            db.close()
        except Exception:
            pass
