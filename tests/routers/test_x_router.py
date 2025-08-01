import io
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import ANY

import src.routers.x_router as x_router_module


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(x_router_module.x_router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_post_simple_tweet_success(monkeypatch, client):
    # stub the XApiService.post_tweet to return a predictable result
    class DummyXService:
        def post_tweet(self, text):
            assert text == "hello world"
            return {"id": "tweet123"}

    monkeypatch.setattr(
        x_router_module,
        "XApiService",
        lambda *args, **kwargs: DummyXService()
    )
    # need to rebind router because XApiService instance was created at import time;
    # rebuild app with fresh router
    app = FastAPI()
    app.include_router(x_router_module.XRouter().router)
    test_client = TestClient(app)

    response = test_client.post("/x/tweet", data={"text": "hello world"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["message"] == "Tweet posted!"
    assert body["tweet_id"] == "tweet123"


def test_post_simple_tweet_missing_text(client):
    # text is required form field; omission yields 422
    response = client.post("/x/tweet", data={})
    assert response.status_code == 422


def test_post_simple_tweet_service_error(monkeypatch, client):
    class FailingService:
        def post_tweet(self, text):
            raise RuntimeError("rate limited")

    monkeypatch.setattr(
        x_router_module,
        "XApiService",
        lambda *args, **kwargs: FailingService()
    )
    app = FastAPI()
    app.include_router(x_router_module.XRouter().router)
    test_client = TestClient(app)

    response = test_client.post("/x/tweet", data={"text": "hi"})
    assert response.status_code == 400
    assert "rate limited" in response.json()["detail"]


def test_post_tweet_with_image_success(monkeypatch, client, tmp_path):
    # stub service to verify it gets called with path and text
    called = {}

    class DummyXService:
        def post_tweet_with_image(self, text, path):
            called["text"] = text
            called["path"] = path
            return {"id": "tweet-img-456"}

    monkeypatch.setattr(
        x_router_module,
        "XApiService",
        lambda *args, **kwargs: DummyXService()
    )
    app = FastAPI()
    app.include_router(x_router_module.XRouter().router)
    test_client = TestClient(app)

    img_bytes = b"\x89PNG\r\n\x1a\n" + b"fakeimage"
    files = {
        "text": (None, "with image"),
        "image": ("test.jpg", io.BytesIO(img_bytes), "image/jpeg"),
    }
    response = test_client.post("/x/tweet-with-image", files=files)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["message"] == "Tweet with image posted!"
    assert body["tweet_id"] == "tweet-img-456"
    assert called["text"] == "with image"
    assert called["path"].endswith(".jpg")
    # temp file should have been cleaned up
    assert not any(p for p in tmp_path.iterdir())  # if uploads in tmp, else rely on no leftover


def test_post_tweet_with_image_missing_fields(client):
    # missing text
    img_bytes = b"\x89PNG\r\n\x1a\n" + b"fakeimage"
    files = {
        "image": ("test.jpg", io.BytesIO(img_bytes), "image/jpeg"),
    }
    resp = client.post("/x/tweet-with-image", files=files)
    assert resp.status_code == 422

    # missing image
    resp2 = client.post("/x/tweet-with-image", data={"text": "foo"})
    assert resp2.status_code == 422


def test_post_tweet_with_image_service_failure(monkeypatch, client):
    class FailingService:
        def post_tweet_with_image(self, text, path):
            raise RuntimeError("upload failed")

    monkeypatch.setattr(
        x_router_module,
        "XApiService",
        lambda *args, **kwargs: FailingService()
    )
    app = FastAPI()
    app.include_router(x_router_module.XRouter().router)
    test_client = TestClient(app)

    img_bytes = b"\x89PNG\r\n\x1a\n" + b"fakeimage"
    files = {
        "text": (None, "failure case"),
        "image": ("test.jpg", io.BytesIO(img_bytes), "image/jpeg"),
    }
    response = test_client.post("/x/tweet-with-image", files=files)
    assert response.status_code == 400
    assert "upload failed" in response.json()["detail"]