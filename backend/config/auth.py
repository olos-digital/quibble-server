from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.database import SessionLocal
from CRUD import crud_auth, crud_posts, crud_user
import os
from dotenv import load_dotenv


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class AuthService:
    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

    def create_access_token(self, data: dict) -> str:
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def get_current_user(self, token: str, db: Session):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = crud_user.get_user_by_username(db, username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_token_dependency(self):
        return self.oauth2_scheme


# Dependency functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Instance to be reused
auth_service = AuthService()


# FastAPI dependency-compatible wrapper
def get_current_user(
    token: str = Depends(auth_service.get_token_dependency()),
    db: Session = Depends(get_db),
):
    return auth_service.get_current_user(token, db)