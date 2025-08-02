from pydantic import BaseModel


class TextGenerationRequest(BaseModel):
	prompt: str
	count: int = 1
	max_tokens: int = 300
