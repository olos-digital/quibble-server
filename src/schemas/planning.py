from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PlannedPostCreate(BaseModel):
	content: str
	scheduled_time: Optional[datetime]
	image_url: Optional[str] = None


class PostPlanCreate(BaseModel):
	account_id: int
	plan_date: datetime


class PlannedPostRead(PlannedPostCreate):
	id: int
	ai_suggested: bool
	image_url: Optional[str] = None


class PostPlanRead(PostPlanCreate):
	id: int
	status: str
	posts: List[PlannedPostRead]
