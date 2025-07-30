from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.utilities.mistral_client import MistralClient


class GenerateRequest(BaseModel):
	prompt: str
	count: int = 1
	max_tokens: int = 300


class MistralRouter:
	def __init__(self, client: MistralClient):
		self.client = client
		self.router = APIRouter(prefix="/mistral", tags=["Mistral"])
		self._attach_routes()

	def _attach_routes(self):
		@self.router.post("/generate")
		async def generate(req: GenerateRequest):
			if not req.prompt.strip():
				raise HTTPException(status_code=400, detail="Prompt is required")

			drafts = self.client.generate_posts(req.prompt, n=req.count)

			result = {"prompt": req.prompt, "posts": drafts}
			self.client.save(req.prompt, result)

			return result