from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db_config import get_db
from src.repositories.user_repo import UserRepository
from src.schemas.user_schemas import UserUpdate, UserOut
from src.services.auth_service import AuthService
from src.services.user_service import UserService


class UserRouter:
	def __init__(self, auth_service: AuthService):
		self.router = APIRouter()
		self.auth_service = auth_service
		self._setup_routes()

	def _setup_routes(self):
		@self.router.get("/me", response_model=UserOut)
		def get_me(
				db: Session = Depends(get_db),
				current_username: str = Depends(self.auth_service.get_current_user),
		):
			user_service = UserService(UserRepository(db))
			user = user_service.get_user_by_username(current_username)
			if not user:
				raise HTTPException(status_code=401, detail="Invalid user")
			return user

		@self.router.put("/me", response_model=UserOut)
		def update_me(
				update: UserUpdate,
				db: Session = Depends(get_db),
				current_username: str = Depends(self.auth_service.get_current_user),
		):
			user_service = UserService(UserRepository(db))
			user = user_service.get_user_by_username(current_username)
			if not user:
				raise HTTPException(status_code=401, detail="Invalid user")
			return user_service.update_user(user, update)
