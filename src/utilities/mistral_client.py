import requests
import os


class MistralClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("❌ MISTRAL_API_KEY not found!")

        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_text(self, prompt: str, model: str = "mistral-medium", max_tokens: int = 300) -> dict:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        resp = requests.post(self.api_url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()