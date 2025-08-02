from typing import Optional, List

from src.database.models.post import Post
from src.database.models.user import User
from src.repositories.post_repo import PostRepository
from src.utilities import logger

logger = logger.setup_logger("PostService logger")

class PostService:
    """
    Service class responsible for business logic related to post operations.
    """

    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo
        logger.info("PostService initialized with PostRepository")

    def create_post(self, user: User, title: str, content: str) -> Post:
        """
        Create a new post tied to a user.

        Args:
            user (User): Owner of the post.
            title (str): Title of the post.
            content (str): Content body of the post.

        Returns:
            Post: The newly created Post instance.
		Raises:
			Exception: If there is an error during creation, it will be logged and raised.
        """
        logger.info(f"Creating post for user_id={user.id}, title={title}")
        
        try:
            post = Post(title=title, content=content, owner_id=user.id)
            created_post = self.post_repo.create(post)
            logger.info(f"Post created successfully with id={created_post.id}")
            return created_post
        
        except Exception as e:
            logger.error(f"Failed to create post for user_id={user.id}: {e}", exc_info=True)
            raise

    def get_post(self, post_id: int) -> Optional[Post]:
        """
        Retrieve a post by its unique ID.

        Args:
            post_id (int): ID of the post to retrieve.

        Returns:
            Optional[Post]: The Post instance if found, else None.

        Raises:
			HTTPException: If the post does not exist, a 404 error is raised.
        """
        logger.info(f"Fetching post with id={post_id}")
        try:
            post = self.post_repo.get_by_id(post_id)
            if post is None:
                logger.warning(f"Post with id={post_id} not found")
            else:
                logger.info(f"Post with id={post_id} retrieved successfully")
            return post
        
        except Exception as e:
            logger.error(f"Error retrieving post with id={post_id}: {e}", exc_info=True)
            raise

    def get_posts(self, category: Optional[str] = None, sort_by: str = "likes") -> List[Post]:
        """
        List posts optionally filtered by category and sorted by likes or newest.

        Args:
            category (Optional[str]): Category filter; if None, no filtering applied.
            sort_by (str): Sorting criterion: "likes" (default) or "newest".

        Returns:
            List[Post]: List of posts matching criteria.

        Raises:
			HTTPException: If an error occurs during retrieval, a 500 error is raised.
        """
        logger.info(f"Listing posts filtered by category='{category}' sorted by '{sort_by}'")
        
        try:
            posts = self.post_repo.list(category=category, sort_by=sort_by)
            logger.info(f"Retrieved {len(posts)} posts")
            return posts
        
        except Exception as e:
            logger.error(f"Error listing posts with category='{category}' and sort_by='{sort_by}': {e}", exc_info=True)
            raise

    def delete_post(self, user: User, post_id: int) -> bool:
        """
        Delete a post if the requesting user is the owner.

        Args:
            user (User): The user requesting the deletion.
            post_id (int): ID of the post to delete.

        Returns:
            bool: True if deletion succeeded; False if not authorized or post not found.

        Raises:
			HTTPException: If an error occurs during deletion, a 500 error is raised.
        """
        logger.info(f"User id={user.id} attempting to delete post id={post_id}")
        try:
            post = self.post_repo.get_by_id(post_id)
            if post and post.owner_id == user.id:
                self.post_repo.delete(post)
                logger.info(f"Post id={post_id} deleted by user id={user.id}")
                return True
            else:
                logger.warning(f"Deletion denied for user id={user.id} on post id={post_id}: " 
                               "Either post not found or user not owner")
                return False
            
        except Exception as e:
            logger.error(f"Error deleting post id={post_id} for user id={user.id}: {e}", exc_info=True)
            raise

    def update_post_image(self, user: User, post_id: int, image_url: str) -> Optional[Post]:
        """
        Update the image URL of a post if the user is the owner.

        Args:
            user (User): The user requesting the update.
            post_id (int): ID of the post to update.
            image_url (str): New image URL to associate with the post.

        Returns:
            Optional[Post]: Updated Post instance if successful; None if unauthorized or post not found.

        Logs:
            Info on attempt and success.
            Warning when post not found or user unauthorized.
            Error with stack trace on unexpected issues.
        """
        logger.info(f"User id={user.id} updating image of post id={post_id}")
        try:
            post = self.post_repo.get_by_id_and_owner(post_id, user.id)
            if not post:
                logger.warning(f"Post id={post_id} not found or user id={user.id} unauthorized to update image")
                return None
            post.image_url = image_url
            updated_post = self.post_repo.update(post)
            logger.info(f"Post id={post_id} image updated successfully")
            return updated_post
        
        except Exception as e:
            logger.error(f"Error updating image for post id={post_id} by user id={user.id}: {e}", exc_info=True)
            raise

    def get_user_posts(self, user: User) -> List[Post]:
        """
        Retrieve all posts owned by a specific user.

        Args:
            user (User): The user whose posts to retrieve.

        Returns:
            List[Post]: List of posts owned by the user.

        Raises:
			HTTPException: If an error occurs during retrieval, a 500 error is raised.
        """
        logger.info(f"Fetching posts for user id={user.id}")
        try:
            # Assuming post_repo.list() fetches all posts; filter by owner here to save repo changes
            posts = self.post_repo.list()
            user_posts = [p for p in posts if p.owner_id == user.id]
            logger.info(f"User id={user.id} has {len(user_posts)} posts")
            return user_posts
        
        except Exception as e:
            logger.error(f"Error fetching posts for user id={user.id}: {e}", exc_info=True)
            raise
