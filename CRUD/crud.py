from sqlalchemy.orm import Session
from database.models import User, Post
from config.config import get_password_hash, verify_password

def create_user(db: Session, username: str, password: str):
    user = User(username=username, hashed_password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_post(db: Session, user: User, title: str, content: str):
    post = Post(title=title, content=content, owner_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def get_posts(db: Session):
    return db.query(Post).all()

def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

def delete_post(db: Session, user: User, post_id: int):
    post = get_post(db, post_id)
    if post and post.owner_id == user.id:
        db.delete(post)
        db.commit()
        return True
    return False