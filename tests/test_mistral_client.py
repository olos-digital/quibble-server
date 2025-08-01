import pytest
from unittest.mock import patch, MagicMock
from src.utilities.mistral_client import MistralClient

@pytest.fixture
def client(tmp_path):
    # tmp_path — временная директория pytest для сохранения файлов
    return MistralClient(hf_token="fake-token", model_id="fake-model", save_dir=str(tmp_path))

@patch("httpx.post")
def test_generate_posts_success(mock_post, client):
    # Мокаем успешный ответ API
    mock_response = MagicMock()
    mock_response.json.return_value = [{"generated_text": "Generated text"}]
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    drafts = client.generate_posts("Hello", n=1, max_tokens=10)
    assert drafts == ["Generated text"]

@patch("httpx.post")
def test_generate_posts_unexpected_format(mock_post, client):
    # Ответ — не список и не dict с generated_text
    mock_response = MagicMock()
    mock_response.json.return_value = {"unexpected": "data"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    drafts = client.generate_posts("Hello")
    assert drafts == ["{'unexpected': 'data'}"] or drafts == [str({"unexpected": "data"})]

@patch("httpx.post")
def test_generate_posts_http_error(mock_post, client):
    from httpx import HTTPStatusError, Response, Request

    response = Response(status_code=401, request=Request("POST", "http://test"))
    mock_post.return_value.raise_for_status.side_effect = HTTPStatusError("Unauthorized", request=response.request, response=response)

    with pytest.raises(RuntimeError) as excinfo:
        client.generate_posts("Hello")

    assert "Mistral API error" in str(excinfo.value)

def test_save_writes_file(tmp_path, client):
    data = {"prompt": "Hello", "posts": ["post1", "post2"]}
    client.save("Hello", data)

    file = tmp_path / "generated_posts.json"
    # Проверим, что файл создан и в нем содержится корректный JSON
    saved_file = client.save_dir / "generated_posts.json"
    assert saved_file.exists()

    content = saved_file.read_text(encoding="utf-8")
    assert '"prompt": "Hello"' in content
    assert '"post1"' in content