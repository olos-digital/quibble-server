import pytest

def test_register_success(client):
    payload = {"username": "alice", "password": "secret123"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["username"] == "alice"
    assert "id" in body
    # assuming your UserOut excludes hashed password
    assert "hashed_password" not in body and "password" not in body

def test_register_duplicate(client):
    payload = {"username": "bob", "password": "p@ssw0rd"}
    resp1 = client.post("/auth/register", json=payload)
    assert resp1.status_code == 200, resp1.text

    resp2 = client.post("/auth/register", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "User already exists"

def test_login_success(client):
    register = {"username": "charlie", "password": "securepwd"}
    client.post("/auth/register", json=register)

    login_payload = {"username": "charlie", "password": "securepwd"}
    resp = client.post("/auth/login", json=login_payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["access_token"] == "fake-jwt-token-for-charlie"
    assert body["token_type"] == "bearer"

def test_login_failure_wrong_password(client):
    register = {"username": "dave", "password": "correct1"}
    client.post("/auth/register", json=register)

    wrong = {"username": "dave", "password": "wrong1"}
    resp = client.post("/auth/login", json=wrong)
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect username or password"

def test_login_failure_nonexistent_user(client):
    resp = client.post("/auth/login", json={"username": "noone", "password": "whatever"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect username or password"