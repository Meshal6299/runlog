import os
import sqlite3


def test_register(client):
    response = client.post(
        "/register",
        json={
            "email": "John@a.com",
            "password": "johndoe1234"
        }
    )

    assert response.status_code == 200
    assert "email" in response.json()

def test_register_duplicate_email(client):
    client.post(
        "/register",
        json={
            "email": "John@a.com",
            "password": "johndoe1234"
        }
    )

    response2 = client.post(
        "/register",
        json={
            "email": "John@a.com",
            "password": "johndoe1234"
        }
    )

    assert response2.status_code == 409

def test_register_short_password(client):
    response = client.post(
        "/register",
        json={
            "email": "John@a.com",
            "password": "john"
       }
    )

    assert response.status_code == 422
    assert "password" in str(response.json()["detail"])


def test_register_stores_hash(client):

    client.post(
        "/register",
        json={
            "email": "John@a.com",
            "password": "johndoe1234"
       }
    )

    conn = sqlite3.connect(os.environ["DATABASE_PATH"])
    row = conn.execute(
        "select password_hash from users where email = ?",
        ("John@a.com",),
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0] != "johndoe1234"

def test_login(client):
    test_creds = {"email": "runner@example.com", "password": "testpass123"}

    client.post("/register", json=test_creds)
    response = client.post("/login", json=test_creds)

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body

def test_login_wrong_password(client):
    test_creds = {"email": "runner@example.com", "password": "testpass123"}

    other_test_creds = {"email": "runner@example.com", "password": "testpass1243"}

    register = client.post("/register", json=test_creds)
    assert register.status_code == 200 

    response = client.post("/login", json=other_test_creds)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_login_wrong_email(client):
    test_creds = {"email": "runner@example.com", "password": "testpass123"}

    other_test_creds = {"email": "runner1@example.com", "password": "testpass123"}

    register = client.post("/register", json=test_creds)
    assert register.status_code == 200

    response = client.post("/login", json=other_test_creds)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"