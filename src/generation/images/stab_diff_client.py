import base64
from typing import Optional

import httpx
from fastapi import HTTPException

from src.schemas.generation_request import ImageGenerationRequest


class ImageGenerationClient:
    """
    Handles all logic for talking to the Hugging Face inference API for image generation.
    """

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-2-1", hf_token: Optional[str] = None):
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}

    async def generate_image(self, req: ImageGenerationRequest) -> str:
        p = req.parameters
        payload = {
            "inputs": req.prompt,
            "parameters": {
                "height": p.height,
                "width": p.width,
                "seed": p.seed,
                "batch_size": p.batch_size,
                "num_inference_steps": p.num_inference_steps,
                "guidance_scale": p.guidance_scale,
            },
            "options": {"wait_for_model": True},
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self.api_url, json=payload, headers=self.headers)
            content_type = resp.headers.get("content-type", "")
            if resp.status_code != 200 or not content_type.startswith("image/"):
                detail = await resp.aread()
                raise HTTPException(status_code=500, detail=detail.decode())
            return base64.b64encode(resp.content).decode("utf-8")