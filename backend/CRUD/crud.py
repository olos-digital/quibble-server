from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from models.post import Post
from config.auth import auth_service
from database.user_schemas import UserUpdate


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

    def get_user_posts(self, user: User) -> list[Post]:
        return self.db.query(Post).filter(Post.owner_id == user.id).all()


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