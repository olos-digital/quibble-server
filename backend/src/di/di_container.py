import os
from huggingface_hub import InferenceClient
from dependency_injector import containers, providers

# Import services: These are core business logic components injected into routers.
from services.linkedin_service import LinkedInApiService
from services.x_service import XApiService
from services.auth_service import AuthService

# Import routers: These define API endpoints and receive injected services for loose coupling.
from routers.auth_router import AuthRouter
from routers.post_router import PostRouter
from routers.user_router import UserRouter
from routers.x_router import XRouter
from routers.linkedin_router import LinkedInRouter
from routers.mistral_router import MistralRouter


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
        secret_key=config.secret_key,  # injected from config for secure key management.
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

    hf_token = os.getenv("HF_API_TOKEN")
    mistral_client = InferenceClient(token=hf_token)
    mistral_router = providers.Singleton(
        MistralRouter,
        client=mistral_client,
        model_id="mistralai/Mistral-7B-v0.1",
        save_dir="generated_posts"
    )
