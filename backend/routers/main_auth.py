from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import user_schemas, post_schemas
from models import user  # base и post не нужны здесь явно
from CRUD import crud_auth, crud_posts, crud_user
from config import auth

router = APIRouter()

@router.post("/register", response_model=user_schemas.UserOut)
def register(user: user_schemas.UserCreate, db: Session = Depends(auth.get_db)):
    db_user = crud_user.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud_user.create_user(db, user.username, user.password)

@router.post("/login", response_model=post_schemas.Token)
def login(user: user_schemas.UserCreate, db: Session = Depends(auth.get_db)):
    auth_user = crud_user.authenticate_user(db, user.username, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = auth.auth_service.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}