from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
	"""
	SQLAlchemy ORM model representing a user in the database.

	This model maps to the 'users' table and includes fields for authentication
	and relationships to posts.

	Attributes:
		id (int): Primary key, auto-incremented.
		username (str): Unique identifier for the user.
		hashed_password (str): Securely stored password hash.
		posts (relationship): One-to-many relationship with Post model.
	"""
	__tablename__ = "users"  # Table name in the database.

	# Primary key: Unique identifier for each user.
	id = Column(Integer, primary_key=True, index=True)

	# Must be unique; indexed for fast lookups in auth queries.
	username = Column(String, unique=True)

	# Stores bcrypt or similar hash for security; never store plain text.
	hashed_password = Column(String)

	# Relationship: Links to posts owned by this user, enabling eager loading in API responses.
	posts = relationship("Post", back_populates="owner")

	# Stored LinkedIn credentials for OAuth authentication.
	linkedin_token = relationship("LiinkedInTokenModel", uselist=False, back_populates="user")

	# Stored X credentials for OAuth authentication.
	x_token = relationship("XTokenModel", uselist=False, back_populates="user")


