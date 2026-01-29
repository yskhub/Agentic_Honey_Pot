import os
import time
from backend.app.db import SessionLocal, Base, engine
from backend.app.db import Message as DBMessage
from sqlalchemy import text


def test_postgres_connection_and_basic_persistence():
    # Expect CI/runner to set DATABASE_URL to a Postgres instance
    db = SessionLocal()
    try:
        # simple query to ensure connectivity
        db.execute(text('SELECT 1'))

        # insert a test message row and read it back
        sid = 'pg-integration-sid'
        m = DBMessage(session_id=sid, sender='tester', text='hello pg', timestamp=None, raw='{}')
        db.add(m)
        db.commit()

        found = db.query(DBMessage).filter(DBMessage.session_id == sid).first()
        assert found is not None
        assert found.text == 'hello pg'
    finally:
        db.close()
