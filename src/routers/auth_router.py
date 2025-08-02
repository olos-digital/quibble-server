from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.database.db_config import get_db
from src.repositories.user_repo import UserRepository
from src.schemas.user_schemas import UserCreate, UserOut
from src.schemas.post_schemas import Token
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.utilities import logger

logger = logger = logger.setup_logger("AuthRouter logger")

class AuthRouter:
	def __init__(self, auth_service: AuthService):
		"""
		Initialize the AuthRouter with the given AuthService.
		"""
		self.router = APIRouter()
		self.auth_service = auth_service
		self._setup_routes()

	def _get_user_service(self, db: Session = Depends(get_db)) -> UserService:
		"""
		Dependency to get a UserService instance.
		"""
		return UserService(UserRepository(db))

	def _setup_routes(self):
		"""
		Set up the authentication routes: register and login.
		"""

		@self.router.post("/register", response_model=UserOut)
		async def register(
			user: UserCreate,
			user_service: UserService = Depends(self._get_user_service),
		):
			"""
			Register a new user.
			"""
			try:
				# Check if user already exists
				if user_service.get_user_by_username(user.username):
					logger.warning(f"Registration attempt with existing username: {user.username}")
					raise HTTPException(status_code=400, detail="User already exists")
				
				# Create new user
				created_user = user_service.create_user(user.username, user.password)
				logger.info(f"User registered successfully: {user.username}")
				return created_user
			
			except HTTPException as e:
				logger.error(f"{str(e)}")
				raise e
			
			except Exception as e:
				logger.error(f"Unexpected error during registration for {user.username}: {str(e)}")
				raise HTTPException(status_code=500, detail="Internal server error")

		@self.router.post("/login", response_model=Token)
		async def login(
			user: UserCreate,
			user_service: UserService = Depends(self._get_user_service),
		):
			"""
			Authenticate user and return access token.
			"""
			try:
				# Authenticate user credentials
				auth_user = user_service.authenticate_user(user.username, user.password)
				if not auth_user:
					logger.warning(f"Failed login attempt for username: {user.username}")
					raise HTTPException(
						status_code=status.HTTP_401_UNAUTHORIZED,
						detail="Incorrect username or password",
					)
				# Create JWT access token
				access_token = self.auth_service.create_access_token({"sub": user.username})
				logger.info(f"User logged in successfully: {user.username}")
				return {"access_token": access_token, "token_type": "bearer"}
			
			except HTTPException as e:
				logger.error(f"{str(e)}")
				raise e
			
			except Exception as e:
				logger.error(f"Unexpected error during login for {user.username}: {str(e)}")
				raise HTTPException(status_code=500, detail="Internal server error")
