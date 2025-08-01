from fastapi import APIRouter, Depends, HTTPException

from src.schemas.user_schemas import UserUpdate, UserOut
from src.services.auth_service import AuthService
from src.services.user_service import UserService

class UserRouter:
    def __init__(self, auth_service: AuthService, user_service: UserService):
        self.router = APIRouter()
        self.auth_service = auth_service
        self.user_service = user_service
        self._setup_routes()

    def _setup_routes(self):
        # encapsulates endpoint handlers for organization.

        @self.router.get("/me", response_model=UserOut)
        def get_me(current_username: str = Depends(self.auth_service.get_current_user)):
            user = self.user_service.get_user_by_username(current_username)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid user")
            return user

        @self.router.put("/me", response_model=UserOut)
        def update_me(
                update: UserUpdate,
                current_username: str = Depends(self.auth_service.get_current_user),
        ):
            user = self.user_service.get_user_by_username(current_username)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid user")
            updated = self.user_service.update_user(user, update)
            return updated