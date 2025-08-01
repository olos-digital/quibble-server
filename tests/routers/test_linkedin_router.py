import io
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import src.services.linkedin_service as linkedin_service
from src.utilities.linkedin_helper import get_linkedin_token
import src.routers.linkedin_router as linkedin_router_module


# helpers reused from your conftest / other tests
def register_and_get_token(client, username, password):
    resp = client.post("/auth/register", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    login = client.post("/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]

def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_post_text_success(monkeypatch, client: TestClient):
    # stub the LinkedIn token dependency so the route gets a token
    client.app.dependency_overrides[get_linkedin_token] = lambda: "linkedin-token-abc"

    called = {}

    class DummyLinkedInApiService:
        def __init__(self, token):
            assert token == "linkedin-token-abc"
        async def post_text(self, caption):
            called["caption"] = caption
            return "urn:li:post:123"

    monkeypatch.setattr(linkedin_router_module, "LinkedInApiService", DummyLinkedInApiService)

    response = client.post("/linkedin/post", data={"caption": "Hello world"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["message"] == "LinkedIn text post created"
    assert body["post_urn"] == "urn:li:post:123"
    assert called["caption"] == "Hello world"


def test_post_text_missing_caption(client: TestClient):
    # no override needed; validation should kick in
    response = client.post("/linkedin/post", data={})
    assert response.status_code == 422  # missing required form field


def test_post_image_success(monkeypatch, client: TestClient):
    client.app.dependency_overrides[get_linkedin_token] = lambda: "linkedin-token-abc"

    called = {}

    class DummyLinkedInApiService:
        def __init__(self, token):
            assert token == "linkedin-token-abc"
        async def post_with_image(self, caption, path):
            called["caption"] = caption
            called["path"] = path
            return "urn:li:imagepost:456"

    monkeypatch.setattr(linkedin_router_module, "LinkedInApiService", DummyLinkedInApiService)


    img_content = b"\x89PNG\r\n\x1a\n" + b"fakeimage"
    files = {
        "caption": (None, "Image caption"),
        "image": ("test.png", io.BytesIO(img_content), "image/png"),
    }
    response = client.post("/linkedin/post-with-image", files=files)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["message"] == "LinkedIn image post created"
    assert body["post_urn"] == "urn:li:imagepost:456"
    assert called["caption"] == "Image caption"
    assert "path" in called and called["path"].endswith(".jpg")


def test_post_image_missing_image(client: TestClient):
    client.app.dependency_overrides[get_linkedin_token] = lambda: "linkedin-token-abc"
    response = client.post("/linkedin/post-with-image", data={"caption": "hi"})
    assert response.status_code == 422  # missing file


def test_post_image_service_failure(monkeypatch, client: TestClient):
    client.app.dependency_overrides[get_linkedin_token] = lambda: "linkedin-token-abc"

    class FailingService:
        def __init__(self, token):
            assert token == "linkedin-token-abc"
        async def post_with_image(self, caption, path):
            raise RuntimeError("API down")

    monkeypatch.setattr(linkedin_router_module, "LinkedInApiService", FailingService)


    img_content = b"\x89PNG\r\n\x1a\n" + b"fakeimage"
    files = {
        "caption": (None, "Caption"),
        "image": ("test.png", io.BytesIO(img_content), "image/png"),
    }
    response = client.post("/linkedin/post-with-image", files=files)
    # expecting 500 if router converts unexpected errors; otherwise adjust to actual behavior
    assert response.status_code == 500, response.text
    detail = response.json().get("detail", "")
    assert "LinkedIn" in detail or "error" in detail.lower()