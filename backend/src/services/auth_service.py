from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

from database.db_config import get_db
from database.models.user import User
from services.user_service import UserService


load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class AuthService:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    
    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

    def create_access_token(self, data: Dict) -> str:
        return jwt.encode(data, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> User:
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
        return self.oauth2_scheme

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
