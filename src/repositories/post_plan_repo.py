from typing import List
from sqlalchemy.orm import Session

from src.database.models.post_planning import PostPlan
from src.repositories.generic_repo import GenericRepo
from src.schemas.planning import PostPlanCreate


class PostPlanRepo(GenericRepo[PostPlan, PostPlanCreate]):
    """
    Repository class for managing PostPlan entities.
    """

    def __init__(self, session: Session):
        super().__init__(session, PostPlan)

    def list_by_account(self, account_id: int) -> List[PostPlan]:
        """
        Retrieve all PostPlan records associated with a specific account ID.

        Args:
            account_id (int): The ID of the account to filter PostPlans by.

        Returns:
            List[PostPlan]: A list of PostPlan objects linked to the given account.
        """
        return self.list(account_id=account_id)
