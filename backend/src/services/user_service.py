from typing import Optional, List
from sqlalchemy.orm import Session
from database.models.user import User
from database.db_config import get_db
from schemas.user_schemas import UserUpdate
from utilities.password_utils import get_password_hash, verify_password  # New import

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, password: str) -> User:
        hashed_password = get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def update_user(self, user: User, updates: UserUpdate) -> User:
        if updates.username:
            user.username = updates.username
        if updates.password:
            user.hashed_password = get_password_hash(updates.password)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_posts(self, user: User) -> List:
        return user.posts
