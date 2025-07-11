from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user, get_password_hash
from backend.database.database import get_db
from backend.CRUD import crud
from pydantic import BaseModel

router = APIRouter()

# Схемы (DTO) для ввода/вывода
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

# Регистрация
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = crud.create_user(db, user.username, hashed_pw)
    return new_user

@router.put("/update", response_model=UserOut)
def update(user: UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        db_user.username = user.username
        db_user.hashed_pw = get_password_hash(user.password)
        db_user.email = user.email

# Получение текущего профиля
@router.get("/me", response_model=UserOut)
def get_me(current_user = Depends(get_current_user)):
    return current_user

# Обновление профиля
@router.put("/me", response_model=UserOut)
def update_me(
    update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if update.username:
        current_user.username = update.username
    if update.password:
        current_user.hashed_password = get_password_hash(update.password)
    db.commit()
    db.refresh(current_user)
    return current_user
