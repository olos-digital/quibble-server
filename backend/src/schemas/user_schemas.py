from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    """
    Base Pydantic model for user data.
    
    This shared model defines the core username field with validation constraints,
    serving as a foundation for inheritance in create, update, and response models.
    It ensures type safety and input sanitization in FastAPI endpoints.
    
    Attributes:
        username (str): User's unique identifier (min 3, max 50 characters).
    """
    username: str = Field(..., min_length=3, max_length=50)  # length constraints.


class UserCreate(UserBase):
    """
    Pydantic model for creating a new user.
    
    Extends UserBase with a required password field, used in FastAPI request
    bodies for registration endpoints to validate and structure input data.
    
    Attributes:
        password (str): User's password (min 6 characters; hashed before storage).
    """
    password: str = Field(..., min_length=6)  # creation with min length.


class UserUpdate(BaseModel):
    """
    Pydantic model for updating user data.
    
    This model allows optional updates to username or password, used in FastAPI
    request bodies for partial updates while enforcing validation on provided fields.
    
    Attributes:
        username (Optional[str]): New username (min 3, max 50 if provided).
        password (Optional[str]): New password (min 6 if provided).
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)


class UserOut(UserBase):
    """
    Pydantic model for user response data.
    
    Extends UserBase with an ID field, used for serializing user data in FastAPI
    responses.
    
    Attributes:
        id (int): Unique identifier for the user.
    """
    id: int
    
    class Config:
        from_attributes = True  # compatibility with ORM models (e.g., SQLAlchemy).
