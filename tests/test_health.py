from fastapi.testclient import TestClient

from runlog.main import app

client = TestClient(app)


def test_readmain():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}