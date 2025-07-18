from fastapi import Depends
from sqlalchemy.orm import Session
from database.database import SessionLocal
from config.auth_service import auth_service


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User auth dependency
def get_current_user(
    token: str = Depends(auth_service.get_token_dependency()),
    db: Session = Depends(get_db),
):
    return auth_service.get_current_user(token, db)