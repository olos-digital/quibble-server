import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock
from src.generation.text.mistral_client import MistralClient
from src.routers.mistral_router import MistralRouter, GenerateRequest


@pytest.fixture
def fake_client():
    client = MagicMock(spec=MistralClient)
    client.generate_posts.return_value = ["generated post"]
    client.save.return_value = None
    return client

@pytest.fixture
def app(fake_client):
    router = MistralRouter(client=fake_client)
    app = FastAPI()
    app.include_router(router.router)
    return app

def test_generate_success(app, fake_client):
    client = TestClient(app)
    response = client.post("/mistral/generate", json={
        "prompt": "Hello",
        "count": 1,
        "max_tokens": 100
    })
    assert response.status_code == 200
    data = response.json()
    assert data["prompt"] == "Hello"
    assert data["posts"] == ["generated post"]
    fake_client.generate_posts.assert_called_once_with("Hello", n=1, max_tokens=100)
    fake_client.save.assert_called_once()

def test_generate_empty_prompt(app):
    client = TestClient(app)
    response = client.post("/mistral/generate", json={
        "prompt": "   ",
        "count": 1,
        "max_tokens": 100
    })
    assert response.status_code == 400
    assert "Prompt is required" in response.json()["detail"]

def test_generate_internal_error(app, fake_client):
    fake_client.generate_posts.side_effect = RuntimeError("API error")
    client = TestClient(app)
    response = client.post("/mistral/generate", json={
        "prompt": "Hello",
        "count": 1,
        "max_tokens": 100
    })
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]