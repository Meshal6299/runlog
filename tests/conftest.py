import pytest
from fastapi.testclient import TestClient

from runlog.database import init_db
from runlog.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    init_db()
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    creds = {"email": "runner@example.com", "password": "testpass123"}
    client.post("/register", json=creds)
    token = client.post("/login", json=creds).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}