from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import user_schemas, post_schemas
from models import user
from config import dependencies
from CRUD import crud_posts
import uuid
import os
import shutil

class PostRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/", response_model=list[post_schemas.Post])
        def list_posts(
            db: Session = Depends(dependencies.get_db),
            category: Optional[str] = Query(None, description="Filter by category"),
            sort_by: Optional[str] = Query("likes", description="Sorting: 'likes' or 'newest'")
        ):
            return crud_posts.get_posts(db, category=category, sort_by=sort_by)

        @self.router.get("/{post_id}", response_model=post_schemas.Post)
        def get_post_by_id(post_id: int, db: Session = Depends(dependencies.get_db)):
            post = crud_posts.get_post(db, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            return post

        @self.router.delete("/{post_id}")
        def delete_post(
            post_id: int,
            db: Session = Depends(dependencies.get_db),
            current_user: user.User = Depends(dependencies.get_current_user)
        ):
            success = crud_posts.delete_post(db, current_user, post_id)
            if not success:
                raise HTTPException(status_code=403, detail="Not allowed or post not found")
            return {"message": "Deleted"}

        @self.router.post("/{post_id}/image", response_model=post_schemas.Post)
        def upload_post_image(
            post_id: int,
            image: UploadFile = File(...),
            db: Session = Depends(dependencies.get_db),
            current_user: user.User = Depends(dependencies.get_current_user)
        ):
            os.makedirs("uploads", exist_ok=True)
            filename = f"{uuid.uuid4().hex}_{image.filename}"
            filepath = os.path.join("uploads", filename)

            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            image_url = f"/uploads/{filename}"
            post = crud_posts.update_post_image(db, current_user, post_id, image_url)
            if not post:
                raise HTTPException(status_code=403, detail="Not allowed or post not found")
            return post

        @self.router.get("/me", response_model=list[post_schemas.Post])
        def get_my_posts(
            db: Session = Depends(dependencies.get_db),
            current_user: user.User = Depends(dependencies.get_current_user)
        ):
            return crud_posts.get_user_posts(db, current_user)