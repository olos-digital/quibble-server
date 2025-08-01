from sqlalchemy.orm import Session
from src.database.models.user import User
from typing import Optional

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def update(self, user: User) -> User:
        self.session.commit()
        self.session.refresh(user)
        return user