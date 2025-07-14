from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from CRUD import crud
from config import auth
from database import models, schemas
from database.database import engine
from config.auth import get_current_user, create_access_token
from services.upload_image_and_post import publish_post_to_linkedin
from fastapi.staticfiles import StaticFiles
import shutil
import uuid
import os
from typing import Optional
from fastapi import Query

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

os.makedirs("uploads", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db, user.username, user.password)

@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    auth_user = crud.authenticate_user(db, user.username, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User)
def update_user_me(
    user_update: schemas.UserUpdate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.update_user(db, current_user, user_update)

@app.get("/users/me/posts", response_model=list[schemas.Post])
def get_my_posts(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_posts(db, current_user)

@app.get("/posts", response_model=list[schemas.Post])
def list_posts(
    db: Session = Depends(auth.get_db),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: Optional[str] = Query("likes", description="Sorting: 'likes' or 'newest'")
):
    return crud.get_posts(db, category=category, sort_by=sort_by)


@app.get("/posts/{post_id}", response_model=schemas.Post)
def get_post_by_id(post_id: int, db: Session = Depends(auth.get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user)
):
    success = crud.delete_post(db, current_user, post_id)
    if not success:
        raise HTTPException(status_code=403, detail="Not allowed or post not found")
    return {"message": "Deleted"}

@app.post("/posts/{post_id}/image", response_model=schemas.Post)
def upload_post_image(
    post_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user)
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

@app.post("/linkedin_post")
def linkedin_post(
    text: str = Form(...),
    image: UploadFile = File(...),
):
    os.makedirs("temp_uploads", exist_ok=True)
    filename = f"temp_{uuid.uuid4().hex}_{image.filename}"
    filepath = os.path.join("temp_uploads", filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    try:
        publish_post_to_linkedin(text=text, image_path=filepath)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    return {"message": "Пост опубликован в LinkedIn"}