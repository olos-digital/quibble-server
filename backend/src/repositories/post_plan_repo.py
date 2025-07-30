from sqlalchemy.orm import Session
from repositories.generic_repo import GenericRepo
from database.models.post_planning import PostPlan
from schemas.planning import PostPlanCreate

class PostPlanRepo(GenericRepo[PostPlan, PostPlanCreate]):
    def __init__(self, session: Session):
        super().__init__(session, PostPlan)

    def list_by_account(self, account_id: int):
        return self.list(account_id=account_id)