TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "secret123",
}


def test_register_success(client):
    resp = client.post("/api/v1/auth/register", json=TEST_USER)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_username(client):
    client.post("/api/v1/auth/register", json=TEST_USER)
    resp = client.post("/api/v1/auth/register", json=TEST_USER)
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"]


def test_register_duplicate_email(client):
    client.post("/api/v1/auth/register", json=TEST_USER)
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "another", "email": "test@example.com", "password": "secret123"},
    )
    assert resp.status_code == 409
    assert "Email already registered" in resp.json()["detail"]


def test_login_success(client):
    client.post("/api/v1/auth/register", json=TEST_USER)
    resp = client.post("/api/v1/auth/login", json=TEST_USER)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json=TEST_USER)
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "email": "test@example.com", "password": "wrongpass"},
    )
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "ghost", "email": "ghost@example.com", "password": "secret123"},
    )
    assert resp.status_code == 401
