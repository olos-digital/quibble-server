from dependency_injector import containers, providers

from services.linkedin_service import LinkedInApiService
from services.x_service import XApiService
from services.auth_service import AuthService

from routers.auth_router import AuthRouter
from routers.post_router import PostRouter
from routers.user_router import UserRouter
from routers.x_router import XRouter
from routers.linkedin_router import LinkedInRouter


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    auth_service = providers.Singleton(
        AuthService,
        secret_key=config.secret_key,
        algorithm=config.algorithm,
    )

    auth_router = providers.Singleton(AuthRouter, auth_service=auth_service)

    post_router = providers.Singleton(PostRouter, auth_service=auth_service)

    user_router = providers.Singleton(UserRouter, auth_service=auth_service)

    x_router = providers.Singleton(XRouter)

    linkedin_router = providers.Singleton(LinkedInRouter)
