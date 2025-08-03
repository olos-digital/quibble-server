from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.models.post_planning import PlannedPost
from src.repositories.generic_repo import GenericRepo
from src.schemas.planning import PlannedPostCreate


class PlannedPostRepo(GenericRepo[PlannedPost, PlannedPostCreate]):
	"""
	Repository class for managing PlannedPost entities, 
	which provides methods to interact with the PlannedPost table in the database

	Attributes:
		session (Session): SQLAlchemy session for database operations.
	"""

	def __init__(self, session: Session):
		super().__init__(session, PlannedPost)

	def list_by_plan(self, plan_id: int) -> List[PlannedPost]:
		"""
		Retrieves a list of planned posts filtered by the specified plan ID.

		Args:
			plan_id (int): The ID of the plan to filter planned posts by.

		Returns:
			list: A list of planned posts associated with the given plan ID.
		"""
		return self.list(plan_id=plan_id)

	def create_with_plan(
			self,
			plan_id: int,
			content: str,
			scheduled_time=None,
			ai_suggested: int = 0,
			image_url: Optional[str] = None,
	) -> PlannedPost:
		"""
		Create a new PlannedPost associated with a given plan, and persist it.

		This method ensures the `plan_id` is set at creation time to satisfy the
		non-null constraint, and wraps the operation in error handling so that
		the session is rolled back on failure.

		Args:
		    image_url (str, optional): The URL of the optional image.
		    plan_id (int): ID of the PostPlan this post belongs to.
		    content (str): The textual content of the planned post.
		    scheduled_time (Optional[datetime], optional): When the post is scheduled to go live.
		        Defaults to None.
		    ai_suggested (int, optional): Flag indicating if the post was suggested by AI (0 or 1).
		        Defaults to 0.

		Returns:
		    PlannedPost: The newly created and persisted PlannedPost instance.

		Raises:
		    SQLAlchemyError: Propagates any database error after rolling back the session.
		"""
		obj = self.model(
			plan_id=plan_id,
			content=content,
			scheduled_time=scheduled_time,
			ai_suggested=ai_suggested,
		)
		if image_url is not None:
			setattr(obj, "image_url", image_url)
		try:
			self.session.add(obj)
			self.session.commit()
			self.session.refresh(obj)
			return obj
		except SQLAlchemyError:
			self.session.rollback()
			raise
