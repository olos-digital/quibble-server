from typing import Optional, List

from src.database.models.user import User
from src.repositories.user_repo import UserRepository
from src.schemas.user_schemas import UserUpdate
from src.utilities.password_utils import get_password_hash, verify_password


class UserService:
	def __init__(self, user_repo: UserRepository):
		self.user_repo = user_repo

	def create_user(self, username: str, password: str) -> User:
		hashed_password = get_password_hash(password)
		user = User(username=username, hashed_password=hashed_password)
		return self.user_repo.create(user)

	def get_user_by_username(self, username: str) -> Optional[User]:
		return self.user_repo.get_by_username(username)

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
		return self.user_repo.update(user)

	def get_user_posts(self, user: User) -> List:
		return user.posts
