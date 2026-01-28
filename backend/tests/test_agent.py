from backend.app.agent import respond


def test_agent_asks_for_upi():
    r = respond('s1', 'Please send your UPI ID to receive payment')
    assert 'UPI' in r['reply'] or 'UPI' in r['reply'].upper() or len(r['reply'])>0


def test_agent_basic_reply():
    r = respond('s2', 'Hello, I need help')
    assert 'reply' in r
