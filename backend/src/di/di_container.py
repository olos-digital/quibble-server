from dependency_injector import containers, providers
from backend.src.services.linkedin_service import LinkedInApiService
from backend.src.services.x_service import XApiService
from services.auth_service import AuthService

from routers.auth_router import AuthRouter
from routers.post_router import PostRouter
from routers.user_router import UserRouter
from routers.x_router import XRouter


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    auth_service = providers.Singleton(
        AuthService,
        secret_key=config.secret_key,
        algorithm=config.algorithm,
    )

    linkedin_service = providers.Singleton(LinkedInApiService)

    linkedin_router = providers.Singleton(
        LinkedInApiService,
        linkedin_service=linkedin_service,
    )

    x_service = providers.Singleton(XApiService)
    x_router = providers.Singleton(
        XRouter,
        x_service=x_service,
    )

    auth_router = providers.Singleton(
        AuthRouter,
        auth_service=auth_service,
    )

    post_router = providers.Singleton(PostRouter)
    user_router = providers.Singleton(UserRouter)