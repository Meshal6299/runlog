def test_create_run(client, auth_headers):
    response = client.post(
        "/runs",
        json={
            "run_date": "2026-11-15",
            "distance_km": 21,
            "duration_seconds": 7550,
        },
        headers = auth_headers
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_create_run_rejects_bad_distance(client, auth_headers):
    response = client.post(
        "/runs",
        json={
            "run_date": "2026-11-15",
            "distance_km": "abc",
            "duration_seconds": 3300,
        },
        headers = auth_headers
    )
    assert response.status_code == 422

def test_create_run_reject_bad_time(client, auth_headers):
    response = client.post(
        "/runs",
        json={
            "run_date": "3333",
            "distance_km": 51,
            "duration_seconds": 99900
        },
        headers = auth_headers
    )
    assert response.status_code == 422

def test_list_runs(client, auth_headers):
    client.post(
        "/runs",
        json={
            "run_date": "2026-11-15",
            "distance_km": 21,
            "duration_seconds": 7550,
        },
        headers = auth_headers
    )
    response = client.get("/runs", headers = auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["distance_km"] == 21

def test_list_runs_no_auth(client, auth_headers):
    client.post(
            "/runs",
            json={
                "run_date": "2026-11-15",
                "distance_km": 21,
                "duration_seconds": 7550,
            },
            headers = auth_headers,
        )

    response = client.get("/runs")

    assert response.status_code == 401

def test_list_runs_bad_token(client, auth_headers):
    client.post(
                "/runs",
                json={
                    "run_date": "2026-11-15",
                    "distance_km": 21,
                    "duration_seconds": 7550,
                },
                headers = auth_headers,
            )
    
    response = client.get(
        "/runs", 
        headers={"Authorization": "Bearer nonsense"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_runs_are_isolated_between_users(client, auth_headers):
    client.post(
        "/runs",
        json={"run_date": "2026-11-15", "distance_km": 10, "duration_seconds": 3000},
        headers=auth_headers,
    )

    creds_b = {"email": "other@example.com", "password": "testpass456"}
    client.post("/register", json=creds_b)
    token_b = client.post("/login", json=creds_b).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. B sees nothing
    response_b = client.get("/runs", headers=headers_b)
    assert response_b.status_code == 200
    assert response_b.json() == []

    # 4. A still sees the run
    response_a = client.get("/runs", headers=auth_headers)
    assert len(response_a.json()) == 1

def test_delete_run(client, auth_headers):
    created = client.post(
        "/runs",
        json={"run_date": "2026-11-15", "distance_km": 10, "duration_seconds": 3000},
        headers=auth_headers, 
    )

    run_id = created.json()["id"]
    assert run_id in [r["id"] for r in client.get("/runs", headers=auth_headers).json()]

    response = client.delete(
        f"/runs/{run_id}",
        headers = auth_headers
    )

    assert response.status_code == 200

    runs = client.get(
        "/runs",
        headers = auth_headers
    ).json()

    ids = [run["id"] for run in runs]
    assert run_id not in ids 

def test_delete_no_run(client, auth_headers):
    response = client.delete(
        "/runs/999999",
        headers = auth_headers
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found"

def test_delete_userA_run_with_userB(client, auth_headers):
    run_a = client.post(
        "/runs",
        json={"run_date": "2026-11-15", "distance_km": 10, "duration_seconds": 3000},
        headers=auth_headers,
    )

    creds_b = {"email": "other@example.com", "password": "testpass456"}
    client.post("/register", json=creds_b)
    token_b = client.post("/login", json=creds_b).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    run_id = run_a.json()["id"]

    response = client.delete(
        f"/runs/{run_id}",
        headers=headers_b
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found"

    response = client.get("/runs", headers=auth_headers)

    assert response.json()[0]["id"] == run_id   



