from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import user_schemas, post_schemas
from models import user, post, base
from config import auth
from CRUD import crud_auth, crud_posts, crud_user

router = APIRouter()

@router.get("/me", response_model=user_schemas.UserOut)
def read_users_me(current_user: user.User = Depends(auth.get_current_user)):
    return current_user

@router.put("/me", response_model=user_schemas.UserOut)
def update_user_me(
    user_update: user_schemas.UserUpdate,
    db: Session = Depends(auth.get_db),
    current_user: user.User = Depends(auth.get_current_user)
):
    return crud_user.update_user(db, current_user, user_update)