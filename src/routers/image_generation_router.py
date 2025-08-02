from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from src.generation.images.stab_diff_client import ImageGenerationClient
from src.schemas.generation_request import ImageGenerationRequest

from src.utilities import logger
logger = logger = logger.setup_logger("ImageGenerationRouter logger")

class ImageGenerationRouter:
    """
    Router for image generation via the Hugging Face Inference API.
    """

    def __init__(self, client: ImageGenerationClient):
        """
        Initialize the router and set up routes.

        Args:
            client (ImageGenerationClient): The client responsible for image generation.
        """
        self.client = client
        self.router = APIRouter(tags=["Image Generation"])
        self._setup_routes()

    def _setup_routes(self):
        """
        Defines the route(s) and their handlers for image generation.
        """

        @self.router.post("/image-generation")
        async def generate_image(request: ImageGenerationRequest) -> dict:
            """
            Endpoint to generate an image from a given request payload.

            Args:
                request (ImageGenerationRequest): The incoming request body with generation parameters.

            Returns:
                dict: A JSON response containing a list of base64-encoded generated images.

            Raises:
                HTTPException: If generation fails, returns a 500 Internal Server Error with a descriptive message.
            """
            logger.info(f"Received image generation request: {request}")

            try:
                # attempt to generate the image asynchronously
                b64_image = await self.client.generate_image(request)
                logger.info("Image generation successful.")
                return {"images": [b64_image]}

            except Exception as e:
                logger.error("Image generation failed", exc_info=True)

                raise HTTPException(
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate image due to an internal error."
                )
