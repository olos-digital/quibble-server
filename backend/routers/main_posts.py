from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import user_schemas, post_schemas
from models import user, post, base
from config import auth
from CRUD import crud
import uuid
import os
import shutil
from typing import Optional
from fastapi import Query

router = APIRouter()

@router.get("/", response_model=list[post_schemas.Post])
def list_posts(
    db: Session = Depends(auth.get_db),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: Optional[str] = Query("likes", description="Sorting: 'likes' or 'newest'")
):
    return crud.get_posts(db, category=category, sort_by=sort_by)

@router.get("/{post_id}", response_model=post_schemas.Post)
def get_post_by_id(post_id: int, db: Session = Depends(auth.get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(auth.get_db),
    current_user: user.User = Depends(auth.get_current_user)
):
    success = crud.delete_post(db, current_user, post_id)
    if not success:
        raise HTTPException(status_code=403, detail="Not allowed or post not found")
    return {"message": "Deleted"}

@router.post("/{post_id}/image", response_model=post_schemas.Post)
def upload_post_image(
    post_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(auth.get_db),
    current_user: user.User = Depends(auth.get_current_user)
):
    os.makedirs("uploads", exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{image.filename}"
    filepath = os.path.join("uploads", filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_url = f"/uploads/{filename}"
    post = crud.update_post_image(db, current_user, post_id, image_url)
    if not post:
        raise HTTPException(status_code=403, detail="Not allowed or post not found")
    return post

@router.get("/me", response_model=list[post_schemas.Post])
def get_my_posts(
    db: Session = Depends(auth.get_db),
    current_user: user.User = Depends(auth.get_current_user)
):
    return crud.get_user_posts(db, current_user)