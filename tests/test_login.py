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