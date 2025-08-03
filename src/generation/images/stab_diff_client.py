import io
import base64
from typing import Optional

from fastapi import HTTPException
from huggingface_hub import AsyncInferenceClient
from src.schemas.generation_request import ImageGenerationRequest
from src.utilities import logger

logger = logger.setup_logger("ImageGenerationClient logger")

FALLBACK_MODELS = [
    "black-forest-labs/FLUX.1-dev",
    "latent-consistency/lcm-lora-sdxl",
    "Kwai-Kolors/Kolors",
    "stabilityai/stable-diffusion-3-medium-diffusers",
]


class ImageGenerationClient:
    """
    Image generation via Hugging Face Inference Providers using the official async client.
    Attempts the primary model, and if unavailable or unsupported falls back to
    recommended alternatives. Provides actionable errors for gating/license issues.
    """

    def __init__(self, model_id: str, hf_token: Optional[str] = None):
        self.model_id = model_id
        self.client = AsyncInferenceClient(model=model_id, token=hf_token, timeout=120)
        logger.info(f"Initialized AsyncInferenceClient for model '{model_id}'")

    async def generate_image(self, req: ImageGenerationRequest) -> str:
        p = req.parameters
        generation_kwargs: dict = {}
        if getattr(p, "height", None) is not None:
            generation_kwargs["height"] = p.height
        if getattr(p, "width", None) is not None:
            generation_kwargs["width"] = p.width
        if getattr(p, "num_inference_steps", None) is not None:
            generation_kwargs["num_inference_steps"] = p.num_inference_steps
        if getattr(p, "guidance_scale", None) is not None:
            generation_kwargs["guidance_scale"] = p.guidance_scale
        if getattr(p, "seed", None) is not None:
            generation_kwargs["seed"] = p.seed

        image = None
        try:
            image = await self.client.text_to_image(req.prompt, **generation_kwargs)
        except Exception as e:
            err_msg = str(e)
            logger.warning(f"Primary model '{self.model_id}' failed to generate image: {err_msg}")

            unsupported = (
                "StopIteration" in err_msg
                or "No Inference Provider" in err_msg
                or "inference is not supported" in err_msg.lower()
            )

            if unsupported:
                for fallback in FALLBACK_MODELS:
                    try:
                        logger.info(f"Falling back to model '{fallback}' after failure on '{self.model_id}'")
                        fallback_client = AsyncInferenceClient(model=fallback, token=self.client.token if hasattr(self.client, "token") else None, timeout=120)
                        image = await fallback_client.text_to_image(req.prompt, **generation_kwargs)
                        self.client = fallback_client
                        self.model_id = fallback
                        break
                    except Exception as e2:
                        logger.warning(f"Fallback model '{fallback}' also failed: {e2}")
                        image = None

                if image is None:
                    raise HTTPException(
                        status_code=502,
                        detail=(
                            f"Image generation failed for primary model '{self.model_id}' and all fallbacks. "
                            "This may be due to the model being unsupported by current inference providers or gated (license/access). "
                            "Visit the model card to accept any license/request access, or try one of the recommended public models from the HF docs: "
                            "black-forest-labs/FLUX.1-dev, latent-consistency/lcm-lora-sdxl, Kwai-Kolors/Kolors, stabilityai/stable-diffusion-3-medium-diffusers. "
                            "See https://huggingface.co/docs/inference-providers/en/tasks/text-to-image for guidance."
                        ),
                    )
            else:
                logger.exception(f"Image generation failed: {err_msg}")
                raise HTTPException(status_code=500, detail=f"Image generation failed: {err_msg}")

        if image is None:
            logger.exception(f"Image generation returned no image.")
            raise HTTPException(status_code=500, detail="Image generation returned no image.")

        try:
            from PIL import Image as PILImage
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="Pillow is required to process the generated image. Install it with `pip install Pillow`.",
            )

        try:
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            logger.info("Image generated and encoded successfully.")
            return b64
        except Exception as e:
            logger.error("Failed to encode image to base64", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to encode the generated image.")