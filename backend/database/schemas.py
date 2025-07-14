from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    class Config:
        from_attributes = True  # ✅ Pydantic v2

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True  # ✅ Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str

class PostCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None