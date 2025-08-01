import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.routers.mistral_router import MistralRouter
from src.schemas.mistral_shemas import PromptRequest

import asyncio


@pytest.fixture
def mistral_client_mock():
    client = MagicMock()
    return client


@pytest.fixture
def test_app(mistral_client_mock):
    router = MistralRouter(mistral_client=mistral_client_mock)
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router.router)
    return app


def test_generate_text_success(test_app, mistral_client_mock):
    # Мокаем возвращаемое значение generate_text
    mistral_client_mock.generate_text.return_value = {
        "choices": [{"message": {"content": "generated response"}}]
    }

    client = TestClient(test_app)

    request_data = {
        "prompt": "Hello world",
        "max_tokens": 5
    }

    response = client.post("/mistral/generate", json=request_data)
    assert response.status_code == 200
    data = response.json()

    assert data["prompt"] == "Hello world"
    assert data["result"] == "generated response"
    assert "raw" in data
    assert data["raw"] == mistral_client_mock.generate_text.return_value
    mistral_client_mock.generate_text.assert_called_once_with("Hello world", max_tokens=5)


def test_generate_text_api_error(test_app, mistral_client_mock):
    mistral_client_mock.generate_text.side_effect = Exception("API failure")

    client = TestClient(test_app)

    request_data = {
        "prompt": "fail prompt",
        "max_tokens": 3
    }

    response = client.post("/mistral/generate", json=request_data)
    assert response.status_code == 502
    assert "Mistral API error: API failure" in response.json()["detail"]
    mistral_client_mock.generate_text.assert_called_once_with("fail prompt", max_tokens=3)