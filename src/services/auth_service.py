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


class AuthService:
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

	def hash_password(self, password: str) -> str:
		return self.pwd_context.hash(password)

	def verify_password(self, plain_password: str, hashed_password: str) -> bool:
		return self.pwd_context.verify(plain_password, hashed_password)

	def create_access_token(
			self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
	) -> str:
		to_encode = data.copy()
		expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
		to_encode.update({"exp": expire})
		return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

	def _decode_token(self, token: str) -> Dict[str, Any]:
		try:
			return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
		except JWTError:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	def get_current_user(
			self,
			token: str = Depends(lambda: None),  # in real wiring override with self.oauth2_scheme
			db: Session = Depends(get_db),
	) -> User:
		if token is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
		payload = self._decode_token(token)
		username: Optional[str] = payload.get("sub")
		if not username:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
		user_service = UserService(UserRepository(db))
		user = user_service.get_user_by_username(username)
		if not user:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
		return user
