from typing import Optional, List

from src.database.models.user import User
from src.schemas.user_schemas import UserUpdate
from sqlalchemy.orm import Session
from src.utilities.password_utils import get_password_hash, verify_password  # New import


class UserService:
    """
    Service class for user operations in FastAPI.
    
    This class provides methods for creating, retrieving, authenticating, updating,
    and fetching posts for users, using an injected database session for transactional
    integrity.
    
    Args:
        db (Session): SQLAlchemy session for database interactions.
    """
    
    def __init__(self, db: Session):
        self.db = db  # Store the session for all operations.
    
    def create_user(self, username: str, password: str) -> User:
        """
        Creates a new user with a hashed password.
        
        This method hashes the password securely, initializes a user, adds it to the database,
        commits the transaction, and refreshes the object for immediate use, aligning with
        FastAPI's ORM patterns for registration flows.
        
        Args:
            username (str): Unique username.
            password (str): Plain password to hash and store.
        
        Returns:
            User: The created user object.
        """
        hashed_password = get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a user by username.
        
        This method queries for a single user, returning None if not found, suitable
        for authentication or lookup in endpoints.
        
        Args:
            username (str): Username to search for.
        
        Returns:
            Optional[User]: The user if found, else None.
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticates a user by username and password.
        
        This method fetches the user and verifies the password hash, returning None
        on failure for secure login handling without revealing existence details.
        
        Args:
            username (str): Username to authenticate.
            password (str): Plain password to verify.
        
        Returns:
            Optional[User]: Authenticated user if valid, else None.
        """
        user = self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    def update_user(self, user: User, updates: UserUpdate) -> User:
        """
        Updates a user's fields based on provided data.
        
        This method applies partial updates (username or password), hashing new passwords,
        commits changes, and refreshes the object for consistency in protected endpoints.
        
        Args:
            user (User): The user to update.
            updates (UserUpdate): Fields to update.
        
        Returns:
            User: The updated user object.
        """
        if updates.username:
            user.username = updates.username
        if updates.password:
            user.hashed_password = get_password_hash(updates.password)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_posts(self, user: User) -> List:
        """
        Retrieves all posts owned by a user.
        
        This method accesses the user's posts via the ORM relationship, suitable
        for user-specific queries in endpoints like profile views.
        
        Args:
            user (User): The user whose posts to fetch.
        
        Returns:
            List: List of user's posts.
        """
        return user.posts
