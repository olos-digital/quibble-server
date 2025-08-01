from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db_config import get_db
from src.repositories.user_repo import UserRepository
from src.schemas import user_schemas, post_schemas
from src.services.auth_service import AuthService
from src.services.user_service import UserService


class AuthRouter:
	def __init__(self, auth_service: AuthService):
		self.router = APIRouter()
		self.auth_service = auth_service
		self._setup_routes()

	def _get_user_service(self, db: Session = Depends(get_db)) -> UserService:
		return UserService(UserRepository(db))

	def _setup_routes(self):
		@self.router.post("/register", response_model=user_schemas.UserOut)
		def register(
				user: user_schemas.UserCreate,
				user_service: UserService = Depends(self._get_user_service),
		):
			if user_service.get_user_by_username(user.username):
				raise HTTPException(status_code=400, detail="User already exists")
			return user_service.create_user(user.username, user.password)

		@self.router.post("/login", response_model=post_schemas.Token)
		def login(
				user: user_schemas.UserCreate,
				user_service: UserService = Depends(self._get_user_service),
		):
			auth_user = user_service.authenticate_user(user.username, user.password)
			if not auth_user:
				raise HTTPException(
					status_code=status.HTTP_401_UNAUTHORIZED,
					detail="Incorrect username or password",
				)
			access_token = self.auth_service.create_access_token({"sub": user.username})
			return {"access_token": access_token, "token_type": "bearer"}
