from backend.phase4.exporter import GuviExporter


def test_exporter_no_endpoint():
    exp = GuviExporter(endpoint=None)
    ok, info = exp.send({"a": 1})
    assert ok is True
    assert info.get("note") == "no-endpoint-stub"


class DummyResp:
    def __init__(self, status=200, text="ok"):
        self.status_code = status
        self.text = text


def test_exporter_http_success(monkeypatch):
    called = {}

    def fake_post(url, json, headers, timeout):
        called["url"] = url
        called["json"] = json
        called["headers"] = headers
        return DummyResp(201, "created")

    monkeypatch.setattr("backend.phase4.exporter.requests.post", fake_post)
    exp = GuviExporter(endpoint="http://example.test/guvi", api_key="key123")
    ok, info = exp.send({"sessionId": "s1"})
    assert ok is True
    assert info["status"] == 201


def test_exporter_http_failure(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResp(500, "error")

    monkeypatch.setattr("backend.phase4.exporter.requests.post", fake_post)
    exp = GuviExporter(endpoint="http://example.test/guvi")
    ok, info = exp.send({})
    assert ok is False
    assert info["status"] == 500
