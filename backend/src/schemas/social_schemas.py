from pydantic import BaseModel, Field
from typing import Optional

class TweetResponse(BaseModel):
    message: str
    tweet_id: str | int