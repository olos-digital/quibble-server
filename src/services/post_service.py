from typing import Optional

from src.database.models.post import Post
from src.database.models.user import User
from sqlalchemy.orm import Session


class PostService:
    """
    Service class for post operations in FastAPI.
    
    This class provides methods for creating, retrieving, listing, deleting, and
    updating posts, using an injected database session for transactional integrity.
    
    Args:
        db (Session): SQLAlchemy session for database interactions.
    """
    
    def __init__(self, db: Session):
        self.db = db  # Store the session for all operations.
    
    def create_post(self, user: User, title: str, content: str) -> Post:
        """
        Creates a new post associated with a user.
        
        This method initializes a post, adds it to the database, commits the transaction,
        and refreshes the object for immediate use, aligning with FastAPI's ORM patterns.
        
        Args:
            user (User): The owner of the post.
            title (str): Post title.
            content (str): Post content.
        
        Returns:
            Post: The created post object.
        """
        post = Post(title=title, content=content, owner_id=user.id)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
    
    def get_post(self, post_id: int) -> Optional[Post]:
        """
        Retrieves a post by ID.
        
        This method queries for a single post, returning None if not found, suitable
        for use in endpoints with 404 handling.
        
        Args:
            post_id (int): ID of the post to fetch.
        
        Returns:
            Optional[Post]: The post if found, else None.
        """
        return self.db.query(Post).filter(Post.id == post_id).first()
    
    def get_posts(self, category: Optional[str] = None, sort_by: str = "likes") -> list[Post]:
        """
        Lists posts with optional filtering and sorting.
        
        This method builds a query with category filtering and sorting (by likes or creation date),
        returning all matching posts. It supports pagination potential in FastAPI endpoints.
        
        Args:
            category (Optional[str]): Filter by category (defaults to None for all).
            sort_by (str): Sorting criteria ('likes' descending or 'newest' by creation date).
        
        Returns:
            list[Post]: List of matching posts.
        """
        query = self.db.query(Post)
        if category:
            query = query.filter(Post.category == category)
        if sort_by == "likes":
            query = query.order_by(Post.likes.desc())
        elif sort_by == "newest":
            query = query.order_by(Post.created_at.desc())
        return query.all()
    
    def delete_post(self, user: User, post_id: int) -> bool:
        """
        Deletes a post if owned by the user.
        
        This method checks ownership before deletion and commits the change, returning
        success status for use in protected endpoints with authorization.
        
        Args:
            user (User): The requesting user.
            post_id (int): ID of the post to delete.
        
        Returns:
            bool: True if deleted, False if not found or not owned.
        """
        post = self.get_post(post_id)
        if post and post.owner_id == user.id:
            self.db.delete(post)
            self.db.commit()
            return True
        return False
    
    def update_post_image(self, user: User, post_id: int, image_url: str) -> Optional[Post]:
        """
        Updates a post's image URL if owned by the user.
        
        This method fetches the post, checks ownership, updates the image URL, commits,
        and refreshes the object, returning None if invalid for error handling in endpoints.
        
        Args:
            user (User): The requesting user.
            post_id (int): ID of the post to update.
            image_url (str): New image URL.
        
        Returns:
            Optional[Post]: Updated post if successful, else None.
        """
        post = self.db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
        if not post:
            return None
        post.image_url = image_url
        self.db.commit()
        self.db.refresh(post)
        return post
