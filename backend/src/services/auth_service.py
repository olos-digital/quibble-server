import os
from typing import Dict

from database.db_config import get_db
from database.models.user import User
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from services.user_service import UserService
from sqlalchemy.orm import Session

# Load environment variables: ensures secrets like keys are available early;
load_dotenv()

# Defines the bearer token mechanism for FastAPI security dependencies.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class AuthService:
    """
    Service class for authentication operations in FastAPI.
    
    This class handles JWT token creation, password hashing/verification, and
    current user retrieval. 
    
    Args:
        secret_key (str): JWT signing key.
        algorithm (str): JWT encoding algorithm (e.g., HS256).
    """
    
    # class-level defaults: Loaded from .env; overridden in __init__ for flexibility.
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    
    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm
        # configured for bcrypt with auto-deprecation for secure hashing.
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # OAuth2 scheme: Reinitialized for token extraction in dependencies.
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
    
    def create_access_token(self, data: Dict) -> str:
        """
        Creates a JWT access token from provided data.
        
        This method encodes payload data (e.g., user claims) into a signed JWT,
        used in login endpoints for session management in FastAPI apps.
        
        Args:
            data (Dict): Payload to encode (e.g., {"sub": username}).
        
        Returns:
            str: Signed JWT token string.
        """
        return jwt.encode(data, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain password against a hashed one.
        
        This utility checks password validity during authentication, using the
        configured CryptContext for secure comparison without exposing hashes.
        
        Args:
            plain_password (str): Input password to verify.
            hashed_password (str): Stored hashed password.
        
        Returns:
            bool: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),  # Injected token from request.
        db: Session = Depends(get_db)  # Injected database session.
    ) -> User:
        """
        Retrieves the current authenticated user from a JWT token.
        
        This dependency function decodes and validates the token, fetches the user
        via UserService, and raises exceptions for invalid cases.
        
        Args:
            token (str): JWT token from the request (via OAuth2 scheme).
            db (Session): Database session for user lookup.
        
        Returns:
            User: Authenticated user object.
        
        Raises:
            HTTPException: 401 for invalid or expired tokens, or if user not found.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_service = UserService(db)
        user = user_service.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    
    def get_token_dependency(self):
        """
        Returns the OAuth2 scheme for use in dependencies.
        
        This method provides the token extraction dependency, useful for custom
        auth flows or overrides in FastAPI routes.
        
        Returns:
            OAuth2PasswordBearer: The configured token scheme.
        """
        return self.oauth2_scheme
    
    def get_password_hash(self, password: str) -> str:
        """
        Hashes a plain password for storage.
        
        This utility generates a secure bcrypt hash, used during user creation
        or updates to store passwords safely.
        
        Args:
            password (str): Plain password to hash.
        
        Returns:
            str: Hashed password string.
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain password against a hashed one (duplicate method).
        
        Note: This is a duplicate of the earlier verify_password; consider removing
        one to avoid redundancy.
        
        Args:
            plain_password (str): Input password.
            hashed_password (str): Stored hash.
        
        Returns:
            bool: True if match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)
