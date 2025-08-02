from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
    prompt: str                       
    positive_prompt: str | None = None # Optional: positive modifier
    negative_prompt: str | None = None # Optional: negative modifier
    width: int = 512                   # Optional: image width in pixels
    height: int = 512                  # Optional: image height in pixels
    num_inference_steps: int = 50      # Optional: diffusion steps
    guidance_scale: float = 7.5        # Optional: CFG/guidance
    seed: int | None = None            # Optional: to reproduce results, else random


class TextGenerationRequest(BaseModel):
	prompt: str
	count: int = 1
	max_tokens: int = 300
