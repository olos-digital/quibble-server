import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Body
from huggingface_hub import InferenceClient


class MistralRouter:
    """
    Router class for text generation using Mistral model.
    """

    def __init__(self, client: InferenceClient, model_id: str, save_dir: str = "generated_posts"):
        self.router = APIRouter(prefix="/mistral", tags=["Mistral"])
        self.client = client
        self.model_id = model_id
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/generate")
        async def generate_post(data: dict = Body(...)):
            """
            Generates text based on a full prompt provided by the user.

            Args:
                data (dict): JSON with "prompt" field.
            """
            prompt = data.get("prompt", "")
            if not prompt:
                raise HTTPException(status_code=400, detail="Prompt is required")

            response = self.client.text_generation(
                model=self.model_id,
                inputs=prompt,
                parameters={"max_new_tokens": 300}
            )

            post_text = getattr(response, "generated_text", response)

            result = {
                "prompt": prompt,
                "post": post_text
            }

            filename = self.save_dir / f"post_{prompt[:20].replace(' ', '_')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            return result