from typing import List

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
	) -> PlannedPost:
		obj = self.model(
			plan_id=plan_id,
			content=content,
			scheduled_time=scheduled_time,
			ai_suggested=ai_suggested,
		)
		try:
			self.session.add(obj)
			self.session.commit()
			self.session.refresh(obj)
			return obj
		except SQLAlchemyError:
			self.session.rollback()
			raise
