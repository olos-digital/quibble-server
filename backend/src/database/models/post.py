from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base  

class Post(Base):
    """
    SQLAlchemy ORM model representing a post in the database.
    
    This model maps to the 'posts' table and includes content fields and a foreign key
    to the User model.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        title (str): Title of the post.
        content (str): Main body/content of the post.
        image_url (str, optional): URL to an associated image.
        owner_id (int): Foreign key referencing the user who owns the post.
        owner (relationship): Many-to-one relationship back to User.
    """
    __tablename__ = "posts" 

    # Primary key: Unique identifier for each post.
    id = Column(Integer, primary_key=True, index=True)
    
    # Required field for post summary.
    title = Column(String)
    
    # Main text body of the post.
    content = Column(String)
    
    # Optional; stores path to uploaded images for media-rich posts.
    image_url = Column(String, nullable=True)
    
    # Foreign key: Links post to its owner, enforcing referential integrity.
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship: Allows navigation from post to owner, useful for API serialization.
    owner = relationship("User", back_populates="posts")
