from fastapi import APIRouter
from src.generation.images.stab_diff_client import ImageGenerationClient
from src.schemas.generation_request import ImageGenerationRequest

class ImageGenerationRouter:
    """
    Router for image generation via Hugging Face Inference API.
    """

    def __init__(self, client: ImageGenerationClient):
        self.client = client
        self.router = APIRouter(tags=["Image Generation"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/image-generation")
        async def generate_image(request: ImageGenerationRequest):
            b64 = await self.client.generate_image(request)
            return {"images": [b64]}