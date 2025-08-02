from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db_config import get_db
from src.database.models.user import User
from src.repositories.user_repo import UserRepository
from src.schemas.user_schemas import UserUpdate, UserOut
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.utilities import logger

logger = logger = logger.setup_logger("UserRouter logger")

class UserRouter:
    """
    Router for user-related endpoints, including retrieving and updating the current user's profile.

    Uses AuthService for authentication and UserService for business logic related to user data.
    """

    def __init__(self, auth_service: AuthService):
        self.router = APIRouter()
        self.auth_service = auth_service
        self._setup_routes()
        logger.info("UserRouter initialized and routes are set up.")

    def _setup_routes(self):
        """
        Attach user-related API endpoints to the router with logging and error handling.
        """

        @self.router.get("/me", response_model=UserOut)
        def get_me(
            db: Session = Depends(get_db),
            current_username: str = Depends(self.auth_service.get_current_user),
        ) -> User:
            """
            Retrieve the current user's profile information.

            Args:
                db (Session): Database session, injected by FastAPI Depends.
                current_username (str): Username of the current authenticated user.

            Returns:
                UserOut: The current user's public profile data.

            Raises:
                HTTPException 401: If the user is not found or invalid.
            """
            logger.info(f"Received get_me request for user: {current_username}")
            try:
                user_service = UserService(UserRepository(db))
                user = user_service.get_user_by_username(current_username)
                
                if not user:
                    logger.warning(f"User not found or invalid: {current_username}")
                    raise HTTPException(status_code=401, detail="Invalid user")
                
                logger.info(f"User profile retrieved successfully for: {current_username}")
                return user

            except HTTPException:
                # known HTTP exception
                raise
            except Exception as e:
                logger.error(f"Unexpected error retrieving user {current_username}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Internal server error")

        @self.router.put("/me", response_model=UserOut)
        def update_me(
            update: UserUpdate,
            db: Session = Depends(get_db),
            current_username: str = Depends(self.auth_service.get_current_user),
        ) -> User:
            """
            Update the current user's profile data.

            Args:
                update (UserUpdate): The data to update for the user.
                db (Session): Database session, injected by FastAPI Depends.
                current_username (str): Username of the current authenticated user.

            Returns:
                UserOut: The updated user profile data.

            Raises:
                HTTPException 401: If the user is not found or invalid.
                HTTPException 500: For unexpected internal errors during update.
            """
            logger.info(f"Received update_me request for user: {current_username} with data: {update}")
            try:
                user_service = UserService(UserRepository(db))
                user = user_service.get_user_by_username(current_username)
                
                if not user:
                    logger.warning(f"User not found or invalid: {current_username}")
                    raise HTTPException(status_code=401, detail="Invalid user")

                updated_user = user_service.update_user(user, update)
                logger.info(f"User profile updated successfully for: {current_username}")
                return updated_user

            except HTTPException:
                # known HTTP exception
                raise
            
            except Exception as e:
                logger.error(f"Unexpected error updating user {current_username}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Internal server error")
