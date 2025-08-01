import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.di.di_container import Container
from src.utilities.exceptions import setup_exception_handlers
from src.routers.mistral_router import MistralRouter

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI app.
    """
    BASE_DIR = Path(__file__).resolve().parent.parent
    default_artifacts = BASE_DIR / "artifacts"

    ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", str(default_artifacts)))

    # Initialize DI container
    container = Container()
    # Load environment variables
    container.config.secret_key.from_env("SECRET_KEY")
    container.config.algorithm.from_env("ALGORITHM")
    container.config.generated_posts_path.from_value(str(ARTIFACTS_DIR / "generated_posts"))
    container.config.mistral_api_key.from_env("MISTRAL_API_KEY")

    app = FastAPI()
    app.container = container

    # Add global exception handlers
    setup_exception_handlers(app)

    # Mount static files
    app.mount(
        "/uploads",
        StaticFiles(directory=str(ARTIFACTS_DIR / "uploads")),
        name="uploads",
    )

    # Include routers
    app.include_router(container.user_router().router, prefix="/users", tags=["users"])
    app.include_router(container.auth_router().router, prefix="/auth", tags=["auth"])
    app.include_router(container.post_router().router, prefix="/posts", tags=["posts"])
    app.include_router(container.linkedin_router().router, prefix="/linkedin", tags=["linkedin"])
    app.include_router(container.x_router().router, prefix="/x", tags=["x"])
    app.include_router(container.image_generation_router().router, tags=["image-generation"])
    app.include_router(container.post_planning_router().router)
    app.include_router(container.mistral_router().router)

    return app


# Global app instance
app = create_app()