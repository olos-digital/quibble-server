from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.db_config import get_db
from src.database.models.user import User
from src.repositories.user_repo import UserRepository
from src.services.user_service import UserService
from src.utilities import logger
from src.exceptions.auth_exception import AuthException

logger = logger.setup_logger("AuthService logger")


class AuthService:
    """
    Service class responsible for authentication-related operations:
    password hashing and verification, access token creation and verification,
    and retrieval of the currently authenticated user.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int = 15,
        token_url: str = "login",
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

        logger.info("AuthService initialized with token expiration set to "
                    f"{self.access_token_expire_minutes} minutes")

    def hash_password(self, password: str) -> str:
        """
        Hashes a plain-text password using bcrypt algorithm.

        Args:
            password (str): Plain-text password to be hashed.

        Returns:
            str: Hashed password.
        """
        hashed = self.pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hashed

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain-text password against its hashed value.

        Args:
            plain_password (str): The plain-text password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if passwords match, False otherwise.
        """
        valid = self.pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {valid}")
        return valid

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Creates a JWT access token with provided data and expiration.

        Args:
            data (Dict[str, Any]): Data to encode inside the token (e.g., subject).
            expires_delta (Optional[timedelta]): Optional expiration time delta. Defaults to class setting.

        Returns:
            str: Encoded JWT token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
        to_encode.update({"exp": expire})

        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Access token created with expiration at {expire.isoformat()}")
        return token

    def _decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodes and verifies a JWT token.

        Args:
            token (str): The JWT token to decode.

        Returns:
            Dict[str, Any]: The payload embedded in the token.

        Raises:
            AuthException: If token is invalid or signature verification fails.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug("JWT token decoded successfully")
            return payload

        except JWTError as e:
            logger.warning(f"JWT decode failed: {e}")
            raise AuthException("Invalid token") from e

    def get_current_user(
        self,
        token: str = Depends(lambda: None),  # in real wiring override with self.oauth2_scheme
        db: Session = Depends(get_db),
    ) -> User:
        """
        Retrieves the currently authenticated user from the JWT token.

        Args:
            token (str): JWT token extracted from the request authorization header.
            db (Session): Database session dependency for fetching the user.

        Returns:
            User: The authenticated User object.

        Raises:
            AuthException: If authentication fails at any step.
        """
        if token is None:
            logger.warning("Attempt to access resource without authentication token")
            raise AuthException("Not authenticated")

        logger.debug(f"Authenticating token: {token[:10]}...")  # Log truncated token for privacy

        payload = self._decode_token(token)

        username: Optional[str] = payload.get("sub")
        if not username:
            logger.warning("Token payload missing subject 'sub' field")
            raise AuthException("Invalid token payload")

        user_service = UserService(UserRepository(db))
        user = user_service.get_user_by_username(username)

        if not user:
            logger.warning(f"User '{username}' from token not found in database")
            raise AuthException("User not found")

        logger.info(f"User '{username}' authenticated successfully")
        return user
