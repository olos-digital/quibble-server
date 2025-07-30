from fastapi import APIRouter, HTTPException
from typing import List

from src.services.post_planning_service import PostPlanningService
from src.schemas.planning import (
    PostPlanCreate,
    PostPlanRead,
    PlannedPostCreate,
    PlannedPostRead,
)


class PostPlanningRouter:
    def __init__(self, service: PostPlanningService):
        self.service = service
        self.router = APIRouter(prefix="/planning", tags=["planning"])
        self._attach_routes()

    def _attach_routes(self):
        @self.router.post("/", response_model=PostPlanRead)
        def create_plan(data: PostPlanCreate):
            try:
                return self.service.create_plan(data)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.post("/{plan_id}/generate", response_model=List[PlannedPostRead])
        def ai_generate(plan_id: int):
            try:
                return self.service.generate_posts(plan_id)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Generation failed")

        @self.router.patch(
            "/{plan_id}/posts/{post_id}", response_model=PlannedPostRead
        )
        def update_post(
            plan_id: int, post_id: int, data: PlannedPostCreate
        ):
            try:
                return self.service.update_post(plan_id, post_id, data)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Update failed")