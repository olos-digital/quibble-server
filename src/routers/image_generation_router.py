from fastapi import APIRouter

from src.generation.images.stab_diff_client import ImageGenerationClient 
from src.schemas.generation_request import ImageGenerationRequest 

class ImageGenerationRouter:
    """
    Router for image generation via Hugging Face Inference API, using an injected ImageGenerationClient.

    All inference and error handling logic lives in the client.
    """
    def __init__(self, client: ImageGenerationClient):
        self.client = client
        self.router = APIRouter(tags=["Image Generation"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/image-generation")
        async def generate_image(request: ImageGenerationRequest):
            generated = await self.client.generate_image(request.prompt)
            return {"images": [generated]}

# Export router for app inclusion
image_generation_router = ImageGenerationRouter(client=ImageGenerationClient()).router

