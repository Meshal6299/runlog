import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from runlog.main import app

SCHEMA = Path(__file__).parent.parent / "schema.sql"


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_file))
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    conn = sqlite3.connect(db_file)
    conn.executescript(SCHEMA.read_text())
    conn.execute("insert into users (email, password_hash) values ('t@t.com', 'x')")
    conn.commit()
    conn.close()
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    creds = {"email": "runner@example.com", "password": "testpass123"}
    client.post("/register", json=creds)
    token = client.post("/login", json=creds).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
