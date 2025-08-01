def register_and_get_token(client, username, password):
	# register via auth router
	resp = client.post("/auth/register", json={"username": username, "password": password})
	assert resp.status_code == 200, resp.text
	login = client.post("/auth/login", json={"username": username, "password": password})
	assert login.status_code == 200, login.text
	return login.json()["access_token"]


def auth_headers(token: str):
	return {"Authorization": f"Bearer {token}"}


def test_get_me_requires_auth(client):
	resp = client.get("/users/me")
	assert resp.status_code == 401


def test_register_and_get_me(client):
	token = register_and_get_token(client, "eve", "strongpass")
	headers = auth_headers(token)
	resp = client.get("/users/me", headers=headers)
	assert resp.status_code == 200
	body = resp.json()
	assert body["username"] == "eve"


def test_update_me_username_and_password(client):
	token = register_and_get_token(client, "frank", "mypassword")
	headers = {"Authorization": f"Bearer {token}"}

	# update username
	update_payload = {"username": "frankie"}
	resp = client.put("/users/me", json=update_payload, headers=headers)
	assert resp.status_code == 200
	assert resp.json()["username"] == "frankie"

	# re-login with new username to get fresh token
	login_resp = client.post("/auth/login", json={"username": "frankie", "password": "mypassword"})
	assert login_resp.status_code == 200, login_resp.text
	new_token = login_resp.json()["access_token"]
	new_headers = {"Authorization": f"Bearer {new_token}"}

	# update password (then login with new one)
	update_payload = {"password": "newpass123"}
	resp = client.put("/users/me", json=update_payload, headers=new_headers)
	assert resp.status_code == 200

	# old password should fail
	resp_old = client.post("/auth/login", json={"username": "frankie", "password": "mypassword"})
	assert resp_old.status_code == 401

	# new password works
	resp_new = client.post("/auth/login", json={"username": "frankie", "password": "newpass123"})
	assert resp_new.status_code == 200
