from typing import Optional
from sqlalchemy.orm import Session
from database.models.user import User
from schemas.user_schemas import UserUpdate
from backend.src.services.auth_service import auth_service

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, password: str) -> User:
        hashed_password = auth_service.get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not auth_service.verify_password(password, user.hashed_password):
            return None
        return user

    def update_user(self, user: User, updates: UserUpdate) -> User:
        if updates.username:
            user.username = updates.username
        if updates.password:
            user.hashed_password = auth_service.get_password_hash(updates.password)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_posts(self, user: User) -> list:
        return user.posts
    
    def get_current_user(
        token: str = Depends(auth_service.get_token_dependency()),
        db: Session = Depends(get_db),
    ):
        return auth_service.get_current_user(token, db)