from sqlalchemy.orm import Session
from repositories.generic_repo import GenericRepo
from database.models.post_planning import PlannedPost
from schemas.planning import PlannedPostCreate

class PlannedPostRepo(GenericRepo[PlannedPost, PlannedPostCreate]):
    def __init__(self, session: Session):
        super().__init__(session, PlannedPost)

    def list_by_plan(self, plan_id: int):
        return self.list(plan_id=plan_id)