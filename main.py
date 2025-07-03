from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import models, schemas, crud, auth
from database import engine
from auth import get_current_user, create_access_token
from upload_image_and_post import publish_post_to_linkedin
from fastapi.responses import HTMLResponse
import shutil
import os
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return {"message": "test"}

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

@app.post("/posts", response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_post(db, current_user, post.title, post.content)

@app.get("/posts", response_model=list[schemas.Post])
def list_posts(db: Session = Depends(auth.get_db)):
    return crud.get_posts(db)

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

@app.post("/linkedin_post")
def linkedin_post(
    text: str = Form(...),
    image: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
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