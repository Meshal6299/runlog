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

def test_create_run_rejects_bad_distance(client, auth_headers): #This test it meant to return a validation error (distance wrong data type)
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

def test_create_run_reject_bad_time(client, auth_headers): #This test it meant to return a validation error (date wrong data type)
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
        headers=auth_headers,                                      # 2. user A's token
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