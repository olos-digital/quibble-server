from fastapi import APIRouter, HTTPException, Depends
from src.utilities.mistral_client import MistralClient
from src.schemas.mistral_shemas import PromptRequest  # updated import


class MistralRouter:
    """
    Router class for Mistral API endpoints.
    """

    def __init__(self, mistral_client: MistralClient):
        self.router = APIRouter(prefix="/mistral", tags=["Mistral"])
        self.mistral_client = mistral_client
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/generate")
        async def generate_text(data: PromptRequest):
            """
            Generate text using Mistral API.
            """
            try:
                result = self.mistral_client.generate_text(
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