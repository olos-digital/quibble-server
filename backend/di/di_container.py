from dependency_injector import containers, providers
from services.linkedin_service import LinkedInService
from config.auth_service import AuthService
from routes.inkedin_router import LinkedInPostRouter
from routes.auth_router import AuthRouter
from routes.post_router import PostRouter
from routes.user_router import UserRouter

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    auth_service = providers.Singleton(
        AuthService,
        secret_key=config.secret_key,
        algorithm=config.algorithm,
    )

    linkedin_service = providers.Singleton(LinkedInService)

    linkedin_router = providers.Singleton(
        LinkedInPostRouter,
        linkedin_service=linkedin_service,
    )

    auth_router = providers.Singleton(
        AuthRouter,
        auth_service=auth_service,
    )

    post_router = providers.Singleton(PostRouter)
    user_router = providers.Singleton(UserRouter)