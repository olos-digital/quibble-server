from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import main_auth, main_users, main_posts, main_linkedin

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(main_auth.router, prefix="/auth", tags=["auth"])
app.include_router(main_users.router, prefix="/users", tags=["users"])
app.include_router(main_posts.router, prefix="/posts", tags=["posts"])
app.include_router(main_linkedin.router, prefix="/linkedin", tags=["linkedin"])