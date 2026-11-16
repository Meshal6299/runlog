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
    conn = sqlite3.connect(db_file)
    conn.executescript(SCHEMA.read_text())
    conn.execute("insert into users (email, password_hash) values ('t@t.com', 'x')")
    conn.commit()
    conn.close()
    return TestClient(app)
