from backend.app.db import SessionLocal, Message

db=SessionLocal()
msgs=db.query(Message).filter(Message.session_id=='e2e-session-001').all()
print('found',len(msgs))
for m in msgs:
    print(m.sender, m.text)
db.close()
