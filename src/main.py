import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.di.di_container import Container

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.

    This function initializes the DI container with environment-based config,
    sets up the app instance, attaches the container, mounts static files, and
    includes routers with prefixes/tags.
    Returns:
        FastAPI: Configured application instance.
    """
    BASE_DIR = Path(__file__).resolve().parent.parent  # src/ → project root
    default_artifacts = BASE_DIR / "artifacts"

    ARTIFACTS_DIR = Path(
        os.getenv("ARTIFACTS_DIR", str(default_artifacts))
    )

    container = Container()
    container.config.secret_key.from_env("SECRET_KEY")
    container.config.algorithm.from_env("ALGORITHM")
    container.config.hf_token.from_env("HF_API_TOKEN")
    container.config.mistral_model_id.from_value("mistralai/Mistral-7B-v0.1")
    container.config.generated_posts_path.from_value(
        str(ARTIFACTS_DIR / "generated_posts")
    )

    app = FastAPI()
    app.container = container

    app.mount("/uploads", StaticFiles(directory=str(ARTIFACTS_DIR / "uploads")), name="uploads")
    app.include_router(container.user_router().router, prefix="/users", tags=["users"])
    app.include_router(container.auth_router().router, prefix="/auth", tags=["auth"])
    app.include_router(container.post_router().router, prefix="/posts", tags=["posts"])
    app.include_router(container.linkedin_router().router)
    app.include_router(container.x_router().router)

    app.include_router(container.image_generation_router().router, prefix="/ai", tags=["image-generation"])
    app.include_router(container.mistral_router().router, prefix="/ai", tags=["mistral"])
    app.include_router(container.post_planning_router().router)
    return app

app = create_app()
