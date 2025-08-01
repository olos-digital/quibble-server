import os
import unittest
from unittest.mock import patch, MagicMock

from src.generation.text.mistral_client import MistralClient


class TestMistralClient(unittest.TestCase):

	@patch.dict(os.environ, {"MISTRAL_API_KEY": "env_api_key"})
	def test_init_with_env_key(self):
		client = MistralClient()
		self.assertEqual(client.api_key, "env_api_key")
		self.assertEqual(client.api_url, "https://api.mistral.ai/v1/chat/completions")
		self.assertIn("Authorization", client.headers)
		self.assertIn("Content-Type", client.headers)

	def test_init_with_argument_key(self):
		client = MistralClient(api_key="arg_api_key")
		self.assertEqual(client.api_key, "arg_api_key")

	@patch.dict(os.environ, {}, clear=True)
	def test_init_no_key_raises(self):
		with self.assertRaises(ValueError) as ctx:
			MistralClient()
		self.assertIn("MISTRAL_API_KEY not found", str(ctx.exception))

	@patch("src.generation.text.mistral_client.requests.post")
	def test_generate_text_success(self, mock_post):
		mock_resp = MagicMock()
		mock_resp.json.return_value = {"result": "some generated text"}
		mock_resp.raise_for_status.return_value = None
		mock_post.return_value = mock_resp

		client = MistralClient(api_key="testkey")
		response = client.generate_text("hello prompt", model="mistral-test", max_tokens=10)

		expected_payload = {
			"model": "mistral-test",
			"messages": [{"role": "user", "content": "hello prompt"}],
			"temperature": 0.7,
			"max_tokens": 10,
		}
		mock_post.assert_called_once_with(client.api_url, headers=client.headers, json=expected_payload)
		self.assertEqual(response, {"result": "some generated text"})

	@patch("src.generation.text.mistral_client.requests.post")
	def test_generate_text_http_error(self, mock_post):
		mock_resp = MagicMock()
		mock_resp.raise_for_status.side_effect = Exception("HTTP error")
		mock_post.return_value = mock_resp

		client = MistralClient(api_key="testkey")
		with self.assertRaises(Exception) as ctx:
			client.generate_text("fail prompt")
		self.assertIn("HTTP error", str(ctx.exception))

	@patch("src.generation.text.mistral_client.MistralClient.generate_text")
	def test_generate_posts(self, mock_generate_text):
		mock_generate_text.side_effect = [
			{"text": "post1"},
			{"text": "post2"},
			{"text": "post3"},
			{"text": "post4"},
			{"text": "post5"},
		]

		client = MistralClient(api_key="testkey")
		posts = client.generate_posts("some prompt", n=5)

		self.assertEqual(len(posts), 5)
		self.assertEqual(posts[0], {"text": "post1"})
		self.assertEqual(posts[-1], {"text": "post5"})
		self.assertEqual(mock_generate_text.call_count, 5)


if __name__ == "__main__":
	unittest.main()
