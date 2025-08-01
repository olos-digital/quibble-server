from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db_config import get_db
from src.database.models.user import User

from src.schemas.user_schemas import UserCreate, UserUpdate, UserOut
from src.services.auth_service import AuthService
from src.services.user_service import UserService

class UserRouter:
    """
    Router class for user-related endpoints in FastAPI.
    
    This class defines routes for registration, self-profile retrieval, and updates,
    injecting AuthService for protected operations.
    
    Args:
        auth_service (AuthService): Injected service for handling authentication.
    """
    
    def __init__(self, auth_service: AuthService):
        self.router = APIRouter()
        self.auth_service = auth_service
        self._setup_routes()  # Internal method to define routes.

    def _setup_routes(self):
        # encapsulates endpoint handlers for organization.
        
        @self.router.get("/me", response_model=UserOut)
        def get_me(current_user: Annotated[User, Depends(self.auth_service.get_current_user)]):
            """
            Retrieves the current user's profile.
            
            This protected endpoint returns the authenticated user's data, relying on
            the injected auth service for token validation and user fetching.
            
            Args:
                current_user (User): Injected authenticated user.
            
            Returns:
                UserOut: User's profile data.
            """
            return current_user
        
        @self.router.put("/me", response_model=UserOut)
        def update_me(
            update: UserUpdate,  # input data for updates.
            db: Annotated[Session, Depends(get_db)],
            current_user: Annotated[User, Depends(self.auth_service.get_current_user)]
        ):
            """
            Updates the current user's profile.
            
            This endpoint allows partial updates to username or password, hashing new
            passwords securely and committing changes transactionally. It ensures only
            the authenticated user can modify their own data.
            
            Args:
                update (UserUpdate): Fields to update (username or password).
                db (Session): Injected database session.
                current_user (User): Injected authenticated user.
            
            Returns:
                UserOut: Updated user data.
            """
            if update.username:
                current_user.username = update.username
            if update.password:
                current_user.hashed_password = AuthService.get_password_hash(update.password)
            db.commit()
            db.refresh(current_user)
            return current_user