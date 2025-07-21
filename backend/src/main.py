from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from di import di_container


def create_app() -> FastAPI:
    container = di_container()
    container.config.secret_key.from_env("SECRET_KEY")
    container.config.algorithm.from_env("ALGORITHM")

    app = FastAPI()

    app.container = container

    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    app.include_router(container.user_router().router, prefix="/users", tags=["users"])
    app.include_router(container.auth_router().router, prefix="/auth", tags=["auth"])
    app.include_router(container.posts_router().router, prefix="/posts", tags=["posts"])
    app.include_router(container.linkedin_router().router, prefix="/linkedin", tags=["linkedin"])

    return app


app = create_app()