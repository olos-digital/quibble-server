import os
import shutil
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query

from src.database.models.user import User
from src.schemas.post_schemas import Post
from src.services.auth_service import AuthService
from src.services.post_service import PostService
from src.utilities import logger

logger = logger = logger.setup_logger("PostRouter logger")


def get_uploads_dir() -> str:
    """
    Retrieve the uploads directory path from environment or default to 'uploads'.

    Returns:
        str: The directory path where uploaded images will be stored.
    """
    return os.getenv("UPLOADS_DIR", "uploads")



class PostRouter:
    """
    Router class to manage post-related API endpoints.
    """

    def __init__(self, auth_service: AuthService, post_service: PostService):
        self.router = APIRouter()
        self.auth_service = auth_service
        self.post_service = post_service
        self._setup_routes()
        logger.debug("PostRouter initialized and routes are set up.")

    def _setup_routes(self):
        """
        Defines and attaches endpoints to the router with proper logging and error handling.
        """

        @self.router.get("/me", response_model=list[Post])
        def get_my_posts(
            current_user: User = Depends(self.auth_service.get_current_user),
        ) -> List[Post]:
            """
            Retrieve posts belonging to the current authenticated user.

            Args:
                current_user (User): Automatically injected the current authenticated user.

            Returns:
                list[Post]: List of posts belonging to the current user.
            """
            logger.info(f"Fetching posts for user ID: {current_user.id}")
            try:
                posts = self.post_service.get_user_posts(current_user)
                logger.info(f"Found {len(posts)} posts for user ID: {current_user.id}")
                return posts
            except Exception as e:
                logger.error(f"Error fetching posts for user ID {current_user.id}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to fetch user posts")

        @self.router.get("/", response_model=list[Post])
        def list_posts(
            category: Optional[str] = Query(None, description="Filter by category"),
            sort_by: Optional[str] = Query("likes", description="Sorting: 'likes' or 'newest'"),
        ) -> List[Post]:
            """
            List posts optionally filtered by category and sorted by likes or newest.

            Args:
                category (Optional[str]): Category to filter posts.
                sort_by (Optional[str]): Sort criterion; 'likes' (default) or 'newest'.

            Returns:
                list[Post]: List of posts matching the criteria.
            """
            logger.info(f"Listing posts with filter category={category} and sort_by={sort_by}")
            try:
                posts = self.post_service.get_posts(category=category, sort_by=sort_by)
                logger.info(f"Returned {len(posts)} posts with category={category} sorted by {sort_by}")
                return posts
            
            except Exception as e:
                logger.error(f"Error listing posts: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to list posts")

        @self.router.get("/{post_id}", response_model=Post)
        def get_post_by_id(post_id: int) -> Post:
            """
            Get a post by its ID.

            Args:
                post_id (int): The identifier of the post to retrieve.

            Returns:
                Post: The requested post object.

            Raises:
                HTTPException 404: If the post does not exist.
            """
            logger.info(f"Fetching post with ID: {post_id}")
            try:
                post_obj = self.post_service.get_post(post_id)
                if not post_obj:
                    logger.warning(f"Post with ID {post_id} not found")
                    raise HTTPException(status_code=404, detail="Post not found")
                logger.info(f"Post with ID {post_id} retrieved successfully")
                return post_obj
            
            except HTTPException:
                # 404 explicitly raised above
                raise
            except Exception as e:
                logger.error(f"Error fetching post with ID {post_id}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to fetch post")

        @self.router.delete("/{post_id}")
        def delete_post(
            post_id: int,
            current_user: User = Depends(self.auth_service.get_current_user),
        ):
            """
            Delete a post owned by the current user.

            Args:
                post_id (int): The identifier of the post to delete.
                current_user (User): The authenticated user attempting deletion.

            Returns:
                dict: Success message.

            Raises:
                HTTPException 403: If user is not allowed to delete or post is not found.
                HTTPException 500: For any unexpected errors during deletion.
            """
            logger.info(f"User ID {current_user.id} attempting to delete post ID {post_id}")
            try:
                success = self.post_service.delete_post(current_user, post_id)
                if not success:
                    logger.warning(f"User ID {current_user.id} not authorized or post ID {post_id} not found")
                    raise HTTPException(status_code=403, detail="Not allowed or post not found")
                logger.info(f"Post ID {post_id} deleted by user ID {current_user.id}")
                return {"message": "Deleted"}
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting post ID {post_id} by user ID {current_user.id}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to delete post")

        @self.router.post("/{post_id}/image", response_model=Post)
        def upload_post_image(
            post_id: int,
            image: UploadFile = File(...),
            current_user: User = Depends(self.auth_service.get_current_user),
        ) -> Post:
            """
            Upload an image and associate it with a post owned by the current user.

            The image is saved in the configured uploads directory with a unique filename.

            Args:
                post_id (int): The identifier of the post to update.
                image (UploadFile): The image file to upload.
                current_user (User): The authenticated user making the upload.

            Returns:
                Post: The updated Post object including the image URL.

            Raises:
                HTTPException 403: If user is unauthorized or post not found.
                HTTPException 500: For IO errors or failures to update the post.
            """
            uploads_dir = get_uploads_dir()
            os.makedirs(uploads_dir, exist_ok=True)

            filename = f"{uuid.uuid4().hex}_{image.filename}"
            filepath = os.path.join(uploads_dir, filename)

            logger.info(f"User ID {current_user.id} uploading image for post ID {post_id} as {filename}")

            try:
                with open(filepath, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                image_url = f"/{uploads_dir}/{filename}"
                updated_post = self.post_service.update_post_image(current_user, post_id, image_url)
                
                if not updated_post:
                    logger.warning(f"User ID {current_user.id} not authorized or post ID {post_id} not found during image update")
                    raise HTTPException(status_code=403, detail="Not allowed or post not found")
                
                logger.info(f"Image uploaded and associated with post ID {post_id} by user ID {current_user.id}")
                return updated_post
            
            except HTTPException:
                # HTTPException raised above
                raise
            
            except Exception as e:
                logger.error(f"Failed to upload image for post ID {post_id} by user ID {current_user.id}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to upload image")
            
            finally:
                # the uploaded file is always closed to avoid resource leaks
                image.file.close()
