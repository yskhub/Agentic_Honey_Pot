import importlib
import json


def test_read_events_roundtrip(tmp_path, monkeypatch):
    # Point the audit module at a temp logs dir and a known HMAC key
    logs_dir = tmp_path / "logs"
    monkeypatch.setenv("LOG_DIR", str(logs_dir))
    monkeypatch.setenv("AUDIT_HMAC_KEY", "testkey")

    # Import and reload to pick up env changes
    import backend.app.audit as audit
    importlib.reload(audit)

    # Append an event and verify read_events returns a valid signed entry
    audit.append_event("test_event", {"k": "v"})
    events = audit.read_events()
    assert len(events) == 1
    assert events[0]["valid"] is True

    parsed = json.loads(events[0]["raw"]) if events[0]["raw"] else {}
    assert parsed.get("type") == "test_event"
    assert parsed.get("payload") == {"k": "v"}
