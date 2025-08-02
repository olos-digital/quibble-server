import os
from dependency_injector import containers, providers

from src.database.db_config import SessionLocal
from src.generation.images.flux_client import FluxImageGenerationClient
from src.generation.text.mistral_client import MistralClient
from src.repositories.planned_post_repo import PlannedPostRepo
from src.repositories.post_plan_repo import PostPlanRepo
from src.repositories.post_repo import PostRepository
from src.routers.auth_router import AuthRouter
from src.routers.image_generation_router import FluxImageRouter
from src.routers.linkedin_router import LinkedInRouter
from src.routers.mistral_router import MistralRouter
from src.routers.post_planning_router import PostPlanningRouter
from src.routers.post_router import PostRouter
from src.routers.user_router import UserRouter
from src.routers.x_router import XRouter
from src.services.auth_service import AuthService
from src.services.post_planning_service import PostPlanningService
from src.services.post_service import PostService
from src.utilities.logger import setup_logger


class Container(containers.DeclarativeContainer):
	"""
	DI container for FastAPI app.
	"""

	config = providers.Configuration()

	db_session = providers.Singleton(SessionLocal)

	# Auth service: Singleton to share a single instance across requests,
	# avoiding repeated initialization of security-sensitive components.
	auth_service = providers.Singleton(
		AuthService,
		secret_key=config.secret_key,
		algorithm=config.algorithm,
	)

	post_repo = providers.Factory(
		PostRepository,
		db=db_session,
	)

	post_service = providers.Singleton(
		PostService,
		post_repo=post_repo
	)

	# Auth router: Injects auth_service for handling authentication endpoints.
	auth_router = providers.Singleton(AuthRouter, auth_service=auth_service)
	post_router = providers.Singleton(PostRouter, auth_service=auth_service, post_service=post_service)
	user_router = providers.Singleton(UserRouter, auth_service=auth_service)
	x_router = providers.Singleton(XRouter)
	linkedin_router = providers.Singleton(LinkedInRouter)

	# --- Mistral integration ---

	mistral_client = providers.Singleton(
		MistralClient,
		api_key=config.mistral_api_key
	)
	mistral_router = providers.Factory(
		MistralRouter,
		mistral_client=mistral_client,
	)

	# --- Post planning ---
	post_planning_repo = providers.Factory(
		PostPlanRepo,
		session=db_session,
	)
	planned_post_repo = providers.Factory(
		PlannedPostRepo,
		session=db_session,
	)
	post_planning_service = providers.Factory(
		PostPlanningService,
		plan_repo=post_planning_repo,
		post_repo=planned_post_repo,
		ai_client=mistral_client,
	)
	post_planning_router = providers.Factory(
		PostPlanningRouter,
		service=post_planning_service,
	)

	logger = providers.Singleton(setup_logger)