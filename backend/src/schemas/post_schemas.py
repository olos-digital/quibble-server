from pydantic import BaseModel
from typing import Optional


class PostBase(BaseModel):
    """
    Base Pydantic model for post data.
    
    This shared model defines common fields for posts, used as a foundation
    for inheritance in create and response models.
    
    Attributes:
        title (str): The title of the post.
        content (str): The main content/body of the post.
    """
    title: str
    content: str


class PostCreate(PostBase):
    """
    Pydantic model for creating a new post.
    
    Extends PostBase with an optional category field, used in FastAPI request
    bodies to validate input during post creation endpoints.
    
    Attributes:
        category (Optional[str]): Optional category for the post (defaults to None).
    """
    category: Optional[str] = None


class Post(PostBase):
    """
    Pydantic model for post responses.
    
    Extends PostBase with an ID field, used for serializing database models
    in FastAPI responses. The Config enables ORM mode for easy conversion from
    SQLAlchemy objects.
    
    Attributes:
        id (int): Unique identifier for the post.
    """
    id: int
    
    class Config:
        from_attributes = True  # enables compatibility with ORM models (e.g., SQLAlchemy).


class Token(BaseModel):
    """
    Pydantic model for authentication tokens.
    
    This model structures JWT token responses in FastAPI auth endpoints,
    providing a standardized format for access tokens returned after login.
    
    Attributes:
        access_token (str): The JWT access token.
        token_type (str): Type of token (e.g., 'bearer').
    """
    access_token: str
    token_type: str
