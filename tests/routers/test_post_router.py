import io
import os
import uuid
import pytest
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from typing import Optional
import types

from src.routers.post_router import PostRouter, get_uploads_dir
from src.services.auth_service import AuthService
from src.schemas import post_schemas

# Dummy user returned by auth
class DummyUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Dummy AuthService with get_current_user dependency signature
class DummyAuthService:
    def create_access_token(self, data: dict):
        return f"token-for-{data.get('sub')}"

    def get_current_user(self):
        return DummyUser(id=42, username="testuser")


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("UPLOADS_DIR", str(tmp_path / "uploads"))
    app = FastAPI()

    auth_service = DummyAuthService()

    # Base dummy post service used by the router directly
    class BaseDummyPostService:
        def get_user_posts(self, user):
            return []

        def get_posts(self, category: Optional[str] = None, sort_by: str = "likes"):
            return []

        def get_post(self, post_id: int):
            return None

        def delete_post(self, user, post_id: int):
            return False

        def update_post_image(self, user, post_id: int, image_url: str):
            return None

    dummy_service = BaseDummyPostService()

    # Inject the dummy post service into router constructor
    post_router = PostRouter(auth_service=auth_service, post_service=dummy_service)
    app.include_router(post_router.router, prefix="/posts", tags=["posts"])

    return TestClient(app), dummy_service


def test_list_posts(client):
    client_obj, post_service = client
    fake_post = {
        "id": 1,
        "title": "Hello",
        "content": "World",
        "likes": 5,
        "image_url": None,
        "owner_id": 42,
    }
    # stub
    post_service.get_posts = lambda category=None, sort_by=None: [fake_post]

    resp = client_obj.get("/posts/?category=tech&sort_by=newest")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body, list)
    assert body[0]["title"] == "Hello"


def test_get_post_by_id_found(client):
    client_obj, post_service = client
    fake_post = {
        "id": 1,
        "title": "Hello",
        "content": "World",
        "likes": 5,
        "image_url": None,
        "owner_id": 42,
    }
    post_service.get_post = lambda post_id: fake_post

    resp = client_obj.get("/posts/1")
    assert resp.status_code == 200
    assert resp.json()["id"] == 1


def test_get_post_by_id_not_found(client):
    client_obj, post_service = client
    post_service.get_post = lambda post_id: None

    resp = client_obj.get("/posts/999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Post not found"


def test_delete_post_success(client):
    client_obj, post_service = client
    post_service.delete_post = lambda user, post_id: True

    resp = client_obj.delete("/posts/5")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Deleted"}


def test_delete_post_forbidden(client):
    client_obj, post_service = client
    post_service.delete_post = lambda user, post_id: False

    resp = client_obj.delete("/posts/5")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not allowed or post not found"


def test_get_my_posts(client):
    client_obj, post_service = client
    fake_post = {
        "id": 1,
        "title": "Hello",
        "content": "World",
        "likes": 5,
        "image_url": None,
        "owner_id": 42,
    }
    post_service.get_user_posts = lambda user: [fake_post]

    resp = client_obj.get("/posts/me")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["title"] == "Hello"


def test_upload_post_image_success(client, tmp_path):
    client_obj, post_service = client
    img_bytes = b"\x89PNG\r\n\x1a\n" + b"fakeimagecontent"
    files = {"image": ("test.png", io.BytesIO(img_bytes), "image/png")}

    updated_dict = {
        "id": 7,
        "title": "Hello",
        "content": "World",
        "likes": 5,
        "image_url": "/uploads/test.png",
        "owner_id": 42,
    }
    post_service.update_post_image = lambda current_user, post_id, image_url: updated_dict

    resp = client_obj.post("/posts/7/image", files=files)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("title") == "Hello"
    image_field = body.get("image_url") or body.get("imageUrl")
    assert image_field == "/uploads/test.png"


def test_upload_post_image_forbidden(client):
    client_obj, post_service = client
    img_bytes = b"\x89PNG\r\n\x1a\n" + b"fakeimagecontent"
    files = {"image": ("test.png", io.BytesIO(img_bytes), "image/png")}

    post_service.update_post_image = lambda user, post_id, image_url: None

    resp = client_obj.post("/posts/7/image", files=files)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not allowed or post not found"