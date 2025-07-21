from typing import Optional
from sqlalchemy.orm import Session
from database.models.post import Post
from database.models.user import User

class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, user: User, title: str, content: str) -> Post:
        post = Post(title=title, content=content, owner_id=user.id)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_post(self, post_id: int) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def get_posts(self, category: Optional[str] = None, sort_by: str = "likes") -> list[Post]:
        query = self.db.query(Post)
        if category:
            query = query.filter(Post.category == category)
        if sort_by == "likes":
            query = query.order_by(Post.likes.desc())
        elif sort_by == "newest":
            query = query.order_by(Post.created_at.desc())
        return query.all()

    def delete_post(self, user: User, post_id: int) -> bool:
        post = self.get_post(post_id)
        if post and post.owner_id == user.id:
            self.db.delete(post)
            self.db.commit()
            return True
        return False

    def update_post_image(self, user: User, post_id: int, image_url: str) -> Optional[Post]:
        post = self.db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
        if not post:
            return None
        post.image_url = image_url
        self.db.commit()
        self.db.refresh(post)
        return post