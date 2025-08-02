from fastapi import APIRouter, HTTPException
from src.schemas.generation_request import ImageGenerationRequest
from src.utilities.image_gen_helper import save_image_bytes

from src.utilities.logger import setup_logger

logger = setup_logger("flux_image_router")

class FluxImageRouter:
	def __init__(self, client):
		"""
		Initialize the FluxImageRouter with a client and set up the API router.
		"""
		self.client = client
		self.router = APIRouter(tags=["FLUX Image Generation"])
		logger.info("FluxImageRouter initialized with client: %s", type(client).__name__)
		self._setup_routes()

	def _setup_routes(self):
		"""
		Define the API endpoints for image generation.
		"""
		@self.router.post("/image-generation")
		async def generate_flux_image(request: ImageGenerationRequest):
			"""
			Endpoint to generate an image using the provided request data.
			Saves the generated image and returns its file path.
			"""
			logger.info("Received image generation request: %s", request)
			try:
				# Generate image bytes using the client and request data
				image_bytes = self.client.generate_image(request)
				logger.info("Image bytes generated successfully")

				# TODO: save imags to S3 bucket and return the URL
				filepath = save_image_bytes(image_bytes)
				logger.info("Image saved at: %s", filepath)

			except Exception as exc:
				logger.critical("Failed to generate or save image: %s", exc, exc_info=True)
				raise HTTPException(status_code=500, detail=str(exc))

			return {"file_path": filepath}
