from sqlalchemy.orm import Session
from database.models import User, Post
from config.auth import get_password_hash, verify_password
from database.schemas import UserUpdate

def update_user(db: Session, user: User, updates: UserUpdate):
    if updates.username:
        user.username = updates.username
    if updates.password:
        user.hashed_password = get_password_hash(updates.password)
    db.commit()
    db.refresh(user)
    return user

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

def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

def get_user_posts(db: Session, user: User):
    return db.query(Post).filter(Post.owner_id == user.id).all()

def update_post_image(db: Session, user: User, post_id: int, image_url: str):
    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
    if not post:
        return None
    post.image_url = image_url
    db.commit()
    db.refresh(post)
    return post