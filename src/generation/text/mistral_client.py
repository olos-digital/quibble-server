import requests
import os


class MistralClient:
    def __init__(self, api_key: str | None = None):
        # Initialize the client with the API key, either passed directly or from environment variables
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            # Raise an error if no API key is provided
            raise ValueError("❌ MISTRAL_API_KEY not found!")

        # Base URL for the Mistral chat completions API
        self.api_url = "https://api.mistral.ai/v1/chat/completions"

        # Headers required for the API call
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_text(self, prompt: str, model: str = "mistral-medium", max_tokens: int = 300) -> dict:
        """
        Sends a request to the Mistral API to generate text based on a prompt.

        :param prompt: The text prompt to send to the model.
        :param model: The Mistral model to use (default: mistral-medium).
        :param max_tokens: Maximum number of tokens to generate in the response.
        :return: The API response as a dictionary.
        """
        # Request payload
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }

        # Make a POST request to the API
        resp = requests.post(self.api_url, headers=self.headers, json=payload)

        # Raise an HTTPError if the request was unsuccessful
        resp.raise_for_status()

        # Return the parsed JSON response
        return resp.json()