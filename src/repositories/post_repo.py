from typing import Optional, List

from sqlalchemy.orm import Session

from src.database.models.post import Post


class PostRepository:
	"""
	Handles direct database interactions for Posts using SQLAlchemy.
	"""

	def __init__(self, db: Session):
		self.db = db

	def create(self, post: Post) -> Post:
		self.db.add(post)
		self.db.commit()
		self.db.refresh(post)
		return post

	def get_by_id(self, post_id: int) -> Optional[Post]:
		return self.db.query(Post).filter(Post.id == post_id).first()

	def list(
			self,
			category: Optional[str] = None,
			sort_by: str = "likes"
	) -> List[Post]:
		query = self.db.query(Post)
		if category:
			query = query.filter(Post.category == category)
		if sort_by == "likes":
			query = query.order_by(Post.likes.desc())
		elif sort_by == "newest":
			query = query.order_by(Post.created_at.desc())
		return query.all()

	def delete(self, post: Post) -> None:
		self.db.delete(post)
		self.db.commit()

	def get_by_id_and_owner(
			self,
			post_id: int,
			owner_id: int
	) -> Optional[Post]:
		return (
			self.db.query(Post)
			.filter(Post.id == post_id, Post.owner_id == owner_id)
			.first()
		)

	def update(self, post: Post) -> Post:
		self.db.commit()
		self.db.refresh(post)
		return post
