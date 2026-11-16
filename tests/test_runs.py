def test_create_run(client):
    response = client.post(
        "/runs",
        json={
            "run_date": "2026-11-15",
            "distance_km": 21,
            "duration_seconds": 7550,
        },
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_create_run_rejects_bad_distance(client): #This test it meant to return a validation error (distance wrong data type)
    response = client.post(
        "/runs",
        json={
            "run_date": "2026-11-15",
            "distance_km": "abc",
            "duration_seconds": 3300,
        },
    )
    assert response.status_code == 422

def test_create_run_reject_bad_time(client): #This test it meant to return a validation error (date wrong data type)
    response = client.post(
        "/runs",
        json={
            "run_date": "3333",
            "distance_km": 51,
            "duration_seconds": 99900
        },
    )
    assert response.status_code == 422

def test_list_runs(client):
    client.post(
        "/runs",
        json={
            "run_date": "2026-11-15",
            "distance_km": 21,
            "duration_seconds": 7550,
        }
    )
    response = client.get("/runs")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["distance_km"] == 21

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

import os
import sqlite3


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
