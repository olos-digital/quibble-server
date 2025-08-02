from typing import List

from fastapi import APIRouter, HTTPException

from src.schemas.planning import (
    PostPlanCreate,
    PostPlanRead,
    PlannedPostCreate,
    PlannedPostRead,
)
from src.services.post_planning_service import PostPlanningService
from src.utilities import logger

logger = logger = logger.setup_logger("PostPlanningRouter logger")

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
            logger.info(f"Received create_plan request: {data}")
            try:
                plan = self.service.create_plan(data)
                logger.info(f"Successfully created plan with ID: {plan.id}")
                return plan
            
            except Exception as e:
                logger.error(f"Error creating plan: {e}", exc_info=True)
                raise HTTPException(status_code=400, detail=str(e))

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
            logger.info(f"Received AI generation request for plan_id: {plan_id}")
            try:
                generated_posts = self.service.generate_posts(plan_id)
                logger.info(f"Successfully generated {len(generated_posts)} posts for plan_id: {plan_id}")
                return generated_posts
            
            except ValueError as e:
                logger.warning(f"Plan not found or invalid input for generation: {e}")
                raise HTTPException(status_code=404, detail=str(e))
            
            except Exception as e:
                logger.error(f"Generation failed for plan_id {plan_id}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Generation failed")

        @self.router.patch("/{plan_id}/posts/{post_id}", response_model=PlannedPostRead)
        def update_post(plan_id: int, post_id: int, data: PlannedPostCreate):
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
            logger.info(f"Received update_post request - plan_id: {plan_id}, post_id: {post_id}, data: {data}")
            try:
                updated_post = self.service.update_post(plan_id, post_id, data)
                logger.info(f"Successfully updated post_id: {post_id} in plan_id: {plan_id}")
                return updated_post
            
            except ValueError as e:
                logger.warning(f"Update failed due to not found: {e}")
                raise HTTPException(status_code=404, detail=str(e))
            
            except Exception as e:
                logger.error(f"Update failed for plan_id {plan_id}, post_id {post_id}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Update failed")