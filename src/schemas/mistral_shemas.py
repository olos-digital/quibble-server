from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
	prompt: str = Field(..., description="Text prompt for generation")
	count: int = Field(1, description="Number of variations to generate")
	max_tokens: int = Field(300, description="Maximum number of tokens in the response")
