import os
import shutil
import uuid
from typing import Annotated, Optional

from src.database.db_config import get_db
from src.database.models import user
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from src.schemas import post_schemas
from src.services.auth_service import AuthService
from src.services.post_service import PostService
from sqlalchemy.orm import Session


class PostRouter:
    """
    Router class for post management endpoints in FastAPI.
    
    This class defines routes for listing, retrieving, deleting, updating, and
    fetching user-specific posts.
    
    Args:
        auth_service (AuthService): Injected service for handling user authentication.
    """
    
    def __init__(self, auth_service: AuthService):
        # configures the APIRouter; prefixes/tags set in main app.
        self.router = APIRouter()
        self.auth_service = auth_service
        self._setup_routes()

    def _setup_routes(self):
        # encapsulates endpoint definitions for better organization.
        
        @self.router.get("/", response_model=list[post_schemas.Post])
        def list_posts(
            db: Session = Depends(get_db),  # injected DB session.
            category: Optional[str] = Query(None, description="Filter by category"),  # optional query param.
            sort_by: Optional[str] = Query("likes", description="Sorting: 'likes' or 'newest'")  # optional with default.
        ):
            """
            Lists posts with optional filtering and sorting.
            
            This endpoint fetches posts from the database, applying filters and sorting
            via the service layer.
            
            Args:
                db (Session): Database session.
                category (Optional[str]): Filter by post category.
                sort_by (Optional[str]): Sort order ('likes' or 'newest').
            
            Returns:
                list[post_schemas.Post]: List of matching posts.
            """
            return PostService.get_posts(db, category=category, sort_by=sort_by)
        
        @self.router.get("/{post_id}", response_model=post_schemas.Post)
        def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
            """
            Retrieves a single post by ID.
            
            This endpoint fetches a post and raises a 404 if not found, aligning with
            RESTful practices in FastAPI for clear error handling.
            
            Args:
                post_id (int): ID of the post to retrieve.
                db (Session): Database session.
            
            Returns:
                post_schemas.Post: The post data.
            
            Raises:
                HTTPException: 404 if the post is not found.
            """
            post = PostService.get_post(db, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            return post
        
        @self.router.delete("/{post_id}")
        def delete_post(
            post_id: int,
            db: Annotated[Session, Depends(get_db)],  # annotated for type clarity.
            current_user: Annotated[user.User, Depends(self.auth_service.get_current_user)]  # protected by auth.
        ):
            """
            Deletes a post if owned by the current user.
            
            This endpoint checks ownership before deletion, using annotated dependencies
            for improved type hinting and FastAPI's security features.
            
            Args:
                post_id (int): ID of the post to delete.
                db (Session): Database session.
                current_user (user.User): Authenticated user.
            
            Returns:
                dict: Success message.
            
            Raises:
                HTTPException: 403 if not allowed or post not found.
            """
            success = PostService.delete_post(db, current_user, post_id)
            if not success:
                raise HTTPException(status_code=403, detail="Not allowed or post not found")
            return {"message": "Deleted"}
        
        @self.router.post("/{post_id}/image", response_model=post_schemas.Post)
        def upload_post_image(
            post_id: int,
            db: Annotated[Session, Depends(get_db)],
            current_user: Annotated[user.User, Depends(self.auth_service.get_current_user)],
            image: UploadFile = File(...)  # Required file upload.
        ):
            """
            Uploads and associates an image with a post.
            
            This endpoint handles file uploads securely, generates unique names, and
            updates the post if owned by the user. It ensures the upload directory exists
            and uses efficient copying to minimize I/O overhead in FastAPI apps.
            
            Args:
                post_id (int): ID of the post to update.
                db (Session): Database session.
                current_user (user.User): Authenticated user.
                image (UploadFile): Image file to upload.
            
            Returns:
                post_schemas.Post: Updated post data.
            
            Raises:
                HTTPException: 403 if not allowed or post not found.
            """
            os.makedirs("uploads", exist_ok=True)  # directory for uploads.
            filename = f"{uuid.uuid4().hex}_{image.filename}"  # filename to prevent collisions.
            filepath = os.path.join("uploads", filename)
            
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)  # stream copy.
            
            image_url = f"/uploads/{filename}"
            post = PostService.update_post_image(db, current_user, post_id, image_url)
            if not post:
                raise HTTPException(status_code=403, detail="Not allowed or post not found")
            return post
        
        @self.router.get("/me", response_model=list[post_schemas.Post])
        def get_my_posts(
            db: Annotated[Session, Depends(get_db)],
            current_user: Annotated[user.User, Depends(self.auth_service.get_current_user)]
        ):
            """
            Retrieves posts owned by the current user.
            
            This protected endpoint fetches user-specific posts, using auth dependencies
            to enforce access control in line with FastAPI's security model.
            
            Args:
                db (Session): Database session.
                current_user (user.User): Authenticated user.
            
            Returns:
                list[post_schemas.Post]: List of user's posts.
            """
            return PostService.get_user_posts(db, current_user)
