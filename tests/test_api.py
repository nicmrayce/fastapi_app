import json
import types
import pytest
from fastapi.testclient import TestClient

# Import the running app
from apiapp.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "app" in data

def test_users_create_and_list():
    good = {"email": "user@example.com", "full_name": "Jane Doe", "is_admin": False}
    r = client.post("/users", json=good)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["email"] == good["email"]
    assert data["full_name"] == good["full_name"]
    assert data["is_admin"] is False
    assert "id" in data

    r2 = client.get("/users")
    assert r2.status_code == 200
    users = r2.json()
    assert any(u["email"] == "user@example.com" for u in users)

def test_users_validation_error():
    bad = {"email": "not-an-email", "full_name": "x"}
    r = client.post("/users", json=bad)
    assert r.status_code == 422

def test_background_enqueues_ok(monkeypatch):
    from apiapp.main import _log_to_s3
    calls = {"n": 0}

    def fake_upload(msg: str) -> None:
        calls["n"] += 1

    monkeypatch.setattr("apiapp.main._log_to_s3", fake_upload)
    r = client.post("/background", params={"msg": "hello"})
    assert r.status_code == 200
    assert r.json() == {"enqueued": True}

@pytest.mark.parametrize("text,expected_key", [
    ("I love FastAPI!", "ok"),
])
def test_hf_sentiment_mocked(monkeypatch, text, expected_key):
    async def fake_sentiment(self, t: str):
        return {"ok": True, "label": "POSITIVE", "score": 0.99, "text": t}

    monkeypatch.setattr("apiapp.services.hf.HuggingFaceClient.sentiment", fake_sentiment)
    r = client.post("/huggingface/sentiment", json={"text": text})
    assert r.status_code == 200
    data = r.json()
    assert expected_key in data
    assert data["label"] in {"POSITIVE", "NEGATIVE"}

def test_sync_http_mocked(monkeypatch):
    class FakeResp:
        status_code = 200

    def fake_get(*args, **kwargs):
        return FakeResp()

    monkeypatch.setattr("apiapp.main.requests_session.get", fake_get, raising=True)

    r = client.get("/sync-http")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["status"] == 200

@pytest.mark.asyncio
async def test_async_http_mocked(monkeypatch):
    class FakeResp:
        status_code = 200

    async def fake_get(*args, **kwargs):
        return FakeResp()

    # ✅ patch the actual async client instance
    monkeypatch.setattr("apiapp.main.async_client.get", fake_get, raising=True)

    r = client.get("/async-http")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["status"] == 200
