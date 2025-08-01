from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from src.utilities.mistral_client import MistralClient


class PromptRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for generation")
    count: int = Field(1, description="Number of variations to generate")
    max_tokens: int = Field(300, description="Maximum number of tokens in the response")


# Dependency function for DI
def get_mistral_client() -> MistralClient:
    return MistralClient()


class MistralRouter:
    """
    Router class for Mistral API endpoints.

    This class encapsulates endpoints for text generation using the Mistral API.
    """

    def __init__(self):
        # Initialize APIRouter with prefix and tags
        self.router = APIRouter(prefix="/mistral", tags=["Mistral"])
        self._setup_routes()

    def _setup_routes(self):
        """
        Register all endpoints for the router.
        """
        @self.router.post("/generate")
        async def generate_text(
            data: PromptRequest,
            mistral_client: MistralClient = Depends(get_mistral_client)
        ):
            """
            Generate text using Mistral API.

            Args:
                data (PromptRequest): Input prompt and options.
                mistral_client (MistralClient): Injected client for API calls.

            Returns:
                dict: Generated text and raw API response.
            """
            try:
                result = mistral_client.generate_text(
                    data.prompt, max_tokens=data.max_tokens
                )
                text = result["choices"][0]["message"]["content"]
                return {
                    "prompt": data.prompt,
                    "result": text,
                    "raw": result
                }
            except Exception as e:
                raise HTTPException(
                    status_code=502, detail=f"Mistral API error: {str(e)}"
                )