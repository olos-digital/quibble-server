from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.auth_service import AuthService
from services.user_service import UserService
from schemas import user_schemas, post_schemas

from database.db_config import get_db


class AuthRouter:
    def __init__(self, auth_service: AuthService):
        self.router = APIRouter()
        self.auth_service = auth_service
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/register", response_model=user_schemas.UserOut)
        def register(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
            db_user = UserService.get_user_by_username(db, user.username)
            if db_user:
                raise HTTPException(status_code=400, detail="User already exists")
            return UserService.create_user(db, user.username, user.password)

        @self.router.post("/login", response_model=post_schemas.Token)
        def login(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
            auth_user = UserService.authenticate_user(db, user.username, user.password)
            if not auth_user:
                raise HTTPException(status_code=401, detail="Incorrect username or password")
            token = self.auth_service.create_access_token({"sub": user.username})
            return {"access_token": token, "token_type": "bearer"}