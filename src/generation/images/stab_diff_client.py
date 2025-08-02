import base64
from typing import Optional

import httpx
from fastapi import HTTPException

from src.schemas.generation_request import ImageGenerationRequest
from src.utilities import logger

logger = logger.setup_logger("ImageGenerationClient logger")

class ImageGenerationClient:
    """
    Handles all logic for talking to the Hugging Face inference API for image generation.
    """

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-2-1", hf_token: Optional[str] = None):
        """
        Initializes the client with the model ID and Hugging Face token.
        """
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
        logger.debug(f"ImageGenerationClient initialized with model_id={model_id}")

    async def generate_image(self, req: ImageGenerationRequest) -> str:
        """
        Sends a request to the Hugging Face API to generate an image based on the provided prompt and parameters.
        Args:
            req (ImageGenerationRequest): The request object containing the prompt and parameters.
        Returns:
            str: Base64 encoded string of the generated image.
        Raises:
            HTTPException: If the API call fails or returns a non-image response.
        """
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
        logger.info(f"Sending image generation request to Hugging Face API: {self.api_url}")
        logger.debug(f"Payload: {payload}")

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(self.api_url, json=payload, headers=self.headers)

        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {e}")
            raise HTTPException(status_code=503, detail="Failed to connect to the image generation service.")

        content_type = resp.headers.get("content-type", "")
        if resp.status_code != 200:
            try:
                detail = await resp.aread()
                error_detail = detail.decode(errors="replace")

            except Exception as e:
                logger.error(f"Failed to read error response: {e}")
                error_detail = "Unknown error"

            logger.error(f"Image generation failed with status {resp.status_code}: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)

        if not content_type.startswith("image/"):
            try:
                detail = await resp.aread()
                error_detail = detail.decode(errors="replace")

            except Exception as e:
                logger.error(f"Failed to read non-image response: {e}")
                error_detail = "Non-image response received"
            logger.error(f"Expected image content-type, got '{content_type}'. Detail: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)

        try:
            encoded_image = base64.b64encode(resp.content).decode("utf-8")
            logger.info("Image generated and encoded successfully.")
            return encoded_image
        
        except Exception as e:
            logger.error(f"Failed to encode image: {e}")
            raise HTTPException(status_code=500, detail="Failed to encode the generated image.")
