from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/sentinel.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, index=True)
    metadata_json = Column("metadata", Text)
    persona = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConversationState(Base):
    __tablename__ = 'conversation_state'
    session_id = Column(String, primary_key=True, index=True)
    turn_count = Column(Integer, default=0)
    last_agent_reply = Column(Text, nullable=True)
    messages_json = Column(Text, nullable=True)  # JSON array of last N messages
    slots_json = Column(Text, nullable=True)     # JSON object for extracted slots
    human_override = Column(Boolean, default=False)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    sender = Column(String)
    text = Column(Text)
    timestamp = Column(DateTime)
    raw = Column(Text)

class Extraction(Base):
    __tablename__ = "extractions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    type = Column(String)
    value = Column(String)
    confidence = Column(Float)


class OutgoingMessage(Base):
    __tablename__ = 'outgoing_messages'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    content = Column(Text)
    status = Column(String, default='queued')
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    from pathlib import Path
    dbfile = Path(DATABASE_URL.replace("sqlite:///", ""))
    dbfile.parent.mkdir(parents=True, exist_ok=True)
    # Create all tables (new tables will be created automatically)
    Base.metadata.create_all(bind=engine)

    # Best-effort migration: add missing columns to existing tables.
    # Using PRAGMA table_info to detect missing columns and ALTER if needed.
    try:
        with engine.begin() as conn:
            # conversation_state additions
            try:
                res = conn.execute("PRAGMA table_info('conversation_state')")
                cols = [r[1] for r in res.fetchall()]
            except Exception:
                cols = []

            if cols:
                if 'messages_json' not in cols:
                    try:
                        conn.execute("ALTER TABLE conversation_state ADD COLUMN messages_json TEXT")
                    except Exception:
                        pass
                if 'slots_json' not in cols:
                    try:
                        conn.execute("ALTER TABLE conversation_state ADD COLUMN slots_json TEXT")
                    except Exception:
                        pass
                if 'human_override' not in cols:
                    try:
                        conn.execute("ALTER TABLE conversation_state ADD COLUMN human_override BOOLEAN DEFAULT 0")
                    except Exception:
                        pass
    except Exception:
        # Silently ignore migration failures (best-effort for local/dev)
        pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Ensure DB and schema up-to-date on import
try:
    init_db()
except Exception:
    pass
