import base64
from typing import Optional

import httpx
from fastapi import HTTPException


class ImageGenerationClient:
	"""
	Handles all logic for talking to the Hugging Face inference API for image generation.
	"""

	def __init__(self, model_id: str = "stabilityai/stable-diffusion-2-1", hf_token: Optional[str] = None):
		self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
		self.headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}

	async def generate_image(self, prompt: str) -> str:
		payload = {
			"inputs": prompt,
			"options": {
				"wait_for_model": True
			}
		}
		async with httpx.AsyncClient(timeout=120) as client:
			resp = await client.post(self.api_url, json=payload, headers=self.headers)
			if resp.status_code != 200 or not resp.headers["content-type"].startswith("image/"):
				detail = await resp.aread()
				raise HTTPException(status_code=500, detail=detail.decode())
			b64img = base64.b64encode(resp.content).decode('utf-8')
			return b64img
