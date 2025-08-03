from typing import List

from fastapi import APIRouter, HTTPException

from src.schemas.planning import (
    PostPlanCreate,
    PostPlanRead,
    PlannedPostCreate,
    PlannedPostRead,
)
from src.services.post_planning_service import PostPlanningService


class PostPlanningRouter:
	"""
	Router class to handle HTTP endpoints related to post planning.
	"""

	def __init__(self, service: PostPlanningService):
		self.service = service
		self.router = APIRouter(prefix="/planning", tags=["planning"])
		self._attach_routes()

	def _attach_routes(self):
		"""
		Attach API endpoint handler functions to the router, including error handling and logging.
		"""
		@self.router.post("/", response_model=PostPlanRead)
		def create_plan(data: PostPlanCreate):
			"""
			 Endpoint to create a new post plan.
			 Args:
			     data (PostPlanCreate): Request payload containing plan creation details.
			 Returns:
			     PostPlanRead: The created post plan response model.
			 Raises:
			     HTTPException 400: If any error occurs during plan creation.
			 """
			try:
				return self.service.create_plan(data)
			except Exception as e:
				raise HTTPException(status_code=400, detail=str(e))

		@self.router.get("/{plan_id}", response_model=PostPlanRead)
		def read_plan(plan_id: int) -> PostPlanRead:
			"""
			 Endpoint to get a plan from plan_id.
			 Args:
				 plan_id (int): Plan id of the plan to get.
			 Returns:
				 PostPlanRead: The retrieved post plan response model.
			 Raises:
				 HTTPException 404: If plan with plan_id doesn't exist.
				 HTTPException 500: If any error occurs during plan creation.
			 """
			try:
				return self.service.get_plan(plan_id)
			except ValueError as e:
				raise HTTPException(status_code=404, detail=str(e))
			except Exception as e:
				raise HTTPException(status_code=500, detail="Failed to fetch plan")

		@self.router.post("/{plan_id}/generate", response_model=List[PlannedPostRead])
		def ai_generate(plan_id: int):
			"""
			Endpoint to generate planned posts for a given post plan using AI.
			Args:
			    plan_id (int): ID of the post plan for which posts should be generated.
			Returns:
			    List[PlannedPostRead]: List of generated planned posts.
			Raises:
			    HTTPException 404: If the specified plan is not found.
			    HTTPException 500: If generation fails due to internal errors.
			"""
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
			"""
			Endpoint to update a specific planned post within a post plan.
			Args:
			    plan_id (int): ID of the post plan the post belongs to.
			    post_id (int): ID of the planned post to update.
			    data (PlannedPostCreate): Data to update the planned post with.
			Returns:
			    PlannedPostRead: The updated planned post.
			Raises:
			    HTTPException 404: If the specified plan or post is not found.
			    HTTPException 500: If the update process fails due to an internal error.
			"""
			try:
				return self.service.update_post(plan_id, post_id, data)
			except ValueError as e:
				raise HTTPException(status_code=404, detail=str(e))
			except Exception as e:
				raise HTTPException(status_code=500, detail="Update failed")
