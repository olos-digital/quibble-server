from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from services.auth_service import get_current_user, get_password_hash
from services.user_service import UserService

from schemas.user_schemas import UserCreate, UserUpdate, UserOut


class UserRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/register", response_model=UserOut)
        def register(user: UserCreate, db: Session = Depends(get_db)):
            db_user = UserService.get_user_by_username(db, user.username)
            if db_user:
                raise HTTPException(status_code=400, detail="Username already registered")
            hashed_pw = get_password_hash(user.password)
            new_user = UserService.create_user(db, user.username, hashed_pw)
            return new_user

        @self.router.get("/me", response_model=UserOut)
        def get_me(current_user=Depends(get_current_user)):
            return current_user

        @self.router.put("/me", response_model=UserOut)
        def update_me(
            update: UserUpdate,
            db: Session = Depends(get_db),
            current_user=Depends(get_current_user)
        ):
            if update.username:
                current_user.username = update.username
            if update.password:
                current_user.hashed_password = get_password_hash(update.password)
            db.commit()
            db.refresh(current_user)
            return current_user