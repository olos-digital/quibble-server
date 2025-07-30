from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PlannedPostCreate(BaseModel):
    content: str
    scheduled_time: Optional[datetime]

class PostPlanCreate(BaseModel):
    account_id: int
    plan_date: datetime

class PlannedPostRead(PlannedPostCreate):
    id: int
    ai_suggested: bool

class PostPlanRead(PostPlanCreate):
    id: int
    status: str
    posts: List[PlannedPostRead]