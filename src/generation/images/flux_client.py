import io
from huggingface_hub import InferenceClient

from src.schemas.generation_request import ImageGenerationRequest
from src.utilities.logger import setup_logger

logger = setup_logger("flux_image_router")

class FluxImageGenerationClient:
    """
    Handles text-to-image generation via the Hugging Face FLUX model.
    """

    def __init__(self, hf_token: str, provider: str = "auto", model_id: str = "black-forest-labs/FLUX.1-dev"):
        """
        Initialize the FluxImageGenerationClient.

        Args:
            hf_token (str): Hugging Face API token for authentication.
            provider (str, optional): Inference provider. Defaults to "auto".
            model_id (str, optional): Model identifier. Defaults to "black-forest-labs/FLUX.1-dev".
        """
        self.model_id = model_id
        try:
            self.client = InferenceClient(provider=provider, token=hf_token)
            logger.info("InferenceClient initialized successfully with model_id '%s'.", model_id)
        except Exception as e:
            logger.critical("Failed to initialize InferenceClient: %s", e, exc_info=True)
            raise

    def generate_image(self, request: ImageGenerationRequest) -> bytes:
        """
        Generate an image from a text prompt using the FLUX model.

        Args:
            request (ImageGenerationRequest): The image generation request containing prompt and parameters.

        Returns:
            bytes: The generated image in PNG format as bytes.
        """
        logger.info("Starting image generation for prompt: '%s'", request.prompt)

        try:
            image = self.client.text_to_image(
                request.prompt,
                model=self.model_id,
                height=request.height,
                width=request.width,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                seed=request.seed,
            )

            if image is None:
                logger.critical("Image generation returned None for prompt: '%s'", request.prompt)
                raise RuntimeError("Image generation failed: returned None")
            
        except Exception as e:
            logger.critical("Exception during image generation: %s", e, exc_info=True)
            raise

        try:
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            logger.info("Image generated and saved to buffer successfully.")
            return buf.getvalue()
        
        except Exception as e:
            logger.critical("Failed to save image to buffer: %s", e, exc_info=True)
            raise
