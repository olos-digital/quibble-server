from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from services.auth_service import AuthService
from services.user_service import UserService
from schemas import user_schemas, post_schemas  
from database.db_config import get_db  


class AuthRouter:
    """
    Router class for authentication endpoints in FastAPI.
    
    This class encapsulates routes for user registration and login, injecting
    an AuthService instance for token management.
    
    Args:
        auth_service (AuthService): Injected service for handling authentication logic.
    """
    
    def __init__(self, auth_service: AuthService):
        # configure the APIRouter without prefixes/tags here;
        self.router = APIRouter()
        self.auth_service = auth_service
        self._setup_routes()  # Internal method to define routes.

    def _setup_routes(self):
        # route setup kept private to encapsulate configuration.
    
        @self.router.post("/register", response_model=user_schemas.UserOut)
        def register(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
            """
            Registers a new user.
            
            This endpoint validates the input, checks for username uniqueness, and creates
            a user record.
            
            Args:
                user (user_schemas.UserCreate): Pydantic model with username and password.
                db (Session): Injected SQLAlchemy session for database operations.
            
            Returns:
                user_schemas.UserOut: The created user data (excluding sensitive fields).
            
            Raises:
                HTTPException: 400 if the username is already taken.
            """
            db_user = UserService.get_user_by_username(db, user.username)
            if db_user:
                raise HTTPException(status_code=400, detail="User already exists")
            return UserService.create_user(db, user.username, user.password)
        
        @self.router.post("/login", response_model=post_schemas.Token)
        def login(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
            """
            Authenticates a user and issues a JWT token.
            
            This endpoint verifies credentials and generates an access token for
            authenticated sessions.
            
            Args:
                user (user_schemas.UserCreate): Pydantic model with username and password.
                db (Session): Injected SQLAlchemy session for user lookup.
            
            Returns:
                post_schemas.Token: JWT access token and type.
            
            Raises:
                HTTPException: 401 for incorrect username or password.
            """
            auth_user = UserService.authenticate_user(db, user.username, user.password)
            if not auth_user:
                raise HTTPException(status_code=401, detail="Incorrect username or password")
            token = self.auth_service.create_access_token({"sub": user.username})
            return {"access_token": token, "token_type": "bearer"}
