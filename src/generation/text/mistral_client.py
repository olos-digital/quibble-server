from huggingface_hub import InferenceClient
from pathlib import Path
import json
from typing import List, Optional

class MistralClient:
    def __init__(self, hf_token: str, model_id: str, save_dir: Optional[str] = None):
        self.client = InferenceClient(token=hf_token)
        self.model_id = model_id
        if save_dir:
            self.save_dir = Path(save_dir)
            self.save_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.save_dir = None

    def generate_text(self, prompt: str, max_new_tokens: int = 300) -> str:
        resp = self.client.text_generation(
            model=self.model_id,
            inputs=prompt,
            parameters={"max_new_tokens": max_new_tokens},
        )
        return getattr(resp, "generated_text", resp)

    def generate_posts(self, prompt: str, n: int = 5) -> List[str]:
        """Generate `n` separate post drafts from one prompt."""
        # simple loop—could be parallelized later
        drafts = []
        for _ in range(n):
            drafts.append(self.generate_text(prompt))
        return drafts

    def save(self, prompt: str, result: dict):
        """Optional: dump to disk if save_dir is set."""
        if not self.save_dir:
            return
        fname = f"post_{prompt[:20].replace(' ', '_')}_{int(Path().stat().st_mtime)}.json"
        path = self.save_dir / fname
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)