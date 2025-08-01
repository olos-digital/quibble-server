from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
	prompt: str
	height: int
	width: int
	seed: int
	batch_size: int
	steps: int
	cfg: float


class TextGenerationRequest(BaseModel):
	prompt: str
	count: int = 1
	max_tokens: int = 300
