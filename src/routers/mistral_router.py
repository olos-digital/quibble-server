from fastapi import APIRouter, HTTPException

from src.generation.text.mistral_client import MistralClient
from src.schemas.mistral_shemas import PromptRequest
from src.utilities import logger 

logger = logger = logger.setup_logger("MistralRouter logger")

class MistralRouter:
    """
    Router class for Mistral API endpoints.
    """

    def __init__(self, mistral_client: MistralClient):
        self.router = APIRouter(prefix="/mistral", tags=["Mistral"])
        self.mistral_client = mistral_client
        self._setup_routes()

    def _setup_routes(self):
        """
        Setup API route handlers.
        """

        @self.router.post("/generate")
        async def generate_text(data: PromptRequest):
            """
            Endpoint to generate text from a prompt using the Mistral API.

            Args:
                data (PromptRequest): Incoming request with prompt and max_tokens.

            Returns:
                dict: Contains the original prompt, generated text, and raw API response.

            Raises:
                HTTPException: If the Mistral API call fails or raises an exception.
            """
            logger.info(f"Received Mistral generate_text request: prompt='{data.prompt}'")

            try:
                # Call the client to generate text
                result = self.mistral_client.generate_text(data.prompt, max_tokens=data.max_tokens)
                text = result["choices"][0]["message"]["content"]

                logger.info("Mistral text generation successful.")
                return {
                    "prompt": data.prompt,
                    "result": text,
                    "raw": result
                }

            except Exception as e:
                # Log exception with traceback
                logger.error("Mistral API error during text generation", exc_info=True)
                raise HTTPException(
                    status_code=502,
                    detail=f"Mistral API error: {str(e)}"
                )
