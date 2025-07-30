from dependency_injector import containers, providers

from database.db_config import SessionLocal
from repositories.planned_post_repo import PlannedPostRepo
from repositories.post_plan_repo import PostPlanRepo
# Import routers: These define API endpoints and receive injected services for loose coupling.
from routers.auth_router import AuthRouter
from routers.linkedin_router import LinkedInRouter
from routers.mistral_router import MistralRouter
from routers.post_planning_router import PostPlanningRouter
from routers.post_router import PostRouter
from routers.user_router import UserRouter
from routers.x_router import XRouter
# Import services: These are core business logic components injected into routers.
from services.auth_service import AuthService
from services.post_planning_service import PostPlanningService
from utilities.mistral_client import MistralClient


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection container for the FastAPI application.

    This declarative container manages providers for services and routers,
    ensuring shared instances (via Singletons) for stateless components to
    optimize resource usage in a request-response cycle.
    """

    # Configuration provider: Loads app-wide settings, e.g., from .env vars.
    config = providers.Configuration()

    # Auth service: Singleton to share a single instance across requests,
    # avoiding repeated initialization of security-sensitive components.
    auth_service = providers.Singleton(
        AuthService,
        secret_key=config.secret_key,
        algorithm=config.algorithm,
    )

    # Auth router: Injects auth_service for handling authentication endpoints.
    auth_router = providers.Singleton(AuthRouter, auth_service=auth_service)

    # Post router: Injects auth_service for protected post-related operations.
    post_router = providers.Singleton(PostRouter, auth_service=auth_service)

    # User router: Injects auth_service for user management with auth checks.
    user_router = providers.Singleton(UserRouter, auth_service=auth_service)

    # X (Twitter) router: No injected dependencies; handles its own service internally.
    x_router = providers.Singleton(XRouter)

    # LinkedIn router: No injected dependencies; manages service per-request.
    linkedin_router = providers.Singleton(LinkedInRouter)

    mistral_client = providers.Singleton(
        MistralClient,
        hf_token=config.hf_token,
        model_id=config.mistral_model_id,
        save_dir=config.generated_posts_path
    )

    mistral_router = providers.Singleton(MistralRouter, client=mistral_client)

    db_session = providers.Singleton(SessionLocal)

    # Post planning dependencies
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