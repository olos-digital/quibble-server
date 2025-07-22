from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from di.di_container import Container


def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    
    This function initializes the DI container with environment-based config,
    sets up the app instance, attaches the container, mounts static files, and
    includes routers with prefixes/tags.
    Returns:
        FastAPI: Configured application instance.
    """
    # loads config from env vars for security-sensitive settings.
    container = Container()
    container.config.secret_key.from_env("SECRET_KEY")
    container.config.algorithm.from_env("ALGORITHM")
    
    app = FastAPI()
    
    app.container = container
    
    # serves uploaded images; adjust directory for production paths.
    app.mount("/uploads", StaticFiles(directory="../uploads"), name="uploads")
    
    # attaches modular endpoint groups with prefixes and tags for OpenAPI docs.
    app.include_router(container.user_router().router, prefix="/users", tags=["users"])
    app.include_router(container.auth_router().router, prefix="/auth", tags=["auth"])
    app.include_router(container.post_router().router, prefix="/posts", tags=["posts"])
    app.include_router(container.linkedin_router().router, prefix="/linkedin", tags=["linkedin"])
    app.include_router(container.x_router().router, prefix="/x", tags=["x"])
    
    return app


# Global app instance: created via factory for potential reuse or overrides (e.g., in tests).
app = create_app()
