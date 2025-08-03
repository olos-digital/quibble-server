from typing import Optional

from pydantic import BaseModel, Field


class Parameters(BaseModel):
	height: int = Field(512, ge=64, le=1024)
	width: int = Field(512, ge=64, le=1024)
	seed: Optional[int] = Field(42)
	batch_size: int = Field(1, ge=1, le=4)
	num_inference_steps: int = Field(30, ge=1, le=150)
	guidance_scale: float = Field(7.5, ge=1.0, le=20.0)


class ImageGenerationRequest(BaseModel):
	prompt: str
	parameters: Parameters = Parameters()


class TextGenerationRequest(BaseModel):
	prompt: str
	count: int = 1
	max_tokens: int = 300


class GeneratePostsRequest(BaseModel):
	count: int = Field(1, ge=1, le=7, description="Number of drafts to generate (1–7)")
	with_image: bool = False
