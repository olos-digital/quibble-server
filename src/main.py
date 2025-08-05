import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.di.di_container import Container
from src.utilities.exception_handlers import setup_exception_handlers
from src.utilities.auth_handler import register_auth_exception_handler
from src.utilities.linkedin_handler import register_linkedin_exception_handler
from src.utilities.value_not_found_handler import register_value_not_found_exception_handler


def create_app() -> FastAPI:
	"""
	Factory function to create and configure the FastAPI app.
	"""
	BASE_DIR = Path(__file__).resolve().parent.parent
	default_artifacts = BASE_DIR / "artifacts"

	ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", str(default_artifacts)))
	LOGS_DIR = BASE_DIR / "logs"
	LOGS_DIR.mkdir(parents=True, exist_ok=True)
	log_file = LOGS_DIR / "app.log"
	log_file.touch(exist_ok=True)
	# Initialize DI container
	container = Container()

	container.config.secret_key.from_env("SECRET_KEY")
	container.config.algorithm.from_env("ALGORITHM")
	container.config.generated_posts_path.from_value(str(ARTIFACTS_DIR / "generated_posts"))
	container.config.mistral_api_key.from_env("MISTRAL_API_KEY")
	container.config.hf_token.from_env("HF_API_KEY")
	container.config.stable_diff_model_id.from_env("STABLE_DIFF_MODEL_ID")
	container.config.generated_posts_path.from_value(
		str(ARTIFACTS_DIR / "generated_posts")
	)

	app = FastAPI()
	app.container = container

	origins = [
		"http://localhost:3000",
		"http://127.0.0.1:3000",
	]
	app.add_middleware(
		CORSMiddleware,
		allow_origins=origins,  # or ["*"] for wide-open during dev
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	# Add global exception handlers
	logger = container.logger()
	setup_exception_handlers(app, logger)
	register_auth_exception_handler(app, logger)
	register_linkedin_exception_handler(app, logger)
	register_value_not_found_exception_handler(app, logger)

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
	app.include_router(container.linkedin_router().router)
	app.include_router(container.x_router().router)

	app.include_router(container.image_generation_router().router, prefix="/ai")
	app.include_router(container.mistral_router().router,  prefix="/ai")
	app.include_router(container.post_planning_router().router)

	return app


app = create_app()