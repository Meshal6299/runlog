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
