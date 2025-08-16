from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse

from sqlalchemy.orm import Session

from src.database.models import User
from src.oauth.linkedin_token import exchange_authorization_code
from src.repositories.linkedin_token_repo import LinkedInTokenRepository
from src.services.linkedin_oauth_service import LinkedInOAuthService
from src.services.auth_service import AuthService
from src.repositories.user_repo import UserRepository
from src.database.db_config import get_db

from src.utilities import logger

logger = logger.setup_logger("LinkedInOAuthRouter logger")

class LinkedInOAuthRouter:
    def __init__(
        self, 
        linkedin_oauth_service: LinkedInOAuthService,
        auth_service: AuthService,
        user_repo: UserRepository,
        linkedin_token_repo: LinkedInTokenRepository
    ):
        self.router = APIRouter(prefix="/auth/linkedin", tags=["LinkedIn OAuth"])
        self.linkedin_oauth_service = linkedin_oauth_service
        self.auth_service = auth_service
        self.user_repo = user_repo
        self.linkedin_token_repo = linkedin_token_repo
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/login")
        def linkedin_login(state: str = "randomstring"):
            url = exchange_authorization_code.get_authorize_url(state)
            logger.info(f"Redirecting to LinkedIn login URL: {url}")
            return RedirectResponse(url)

        @self.router.get("/callback")
        def linkedin_callback(
            code: str,
            current_user: User = Depends(self.auth_service.get_current_user),
        ):
            try:
                # Exchange code for token and store
                token = exchange_authorization_code(code, user_id=current_user.id, linkedin_token_repo=self.linkedin_token_repo)

                # Attempt to find the user by LinkedIn URN
                user = self.user_repo.get_by_linkedin_urn(token.owner_urn)
                logger.info(f"LinkedIn token received for user: {token.owner_urn}")

                if not user:
                    username = f"li_{token.owner_urn.replace('urn:li:', '')}"
                    # Create new user
                    user = self.user_repo.create(User(username=username, hashed_password=token.access_token))

                # Save token linked to user
                linkedin_oauth_service = LinkedInOAuthService(user_repo=self.user_repo)
                linkedin_oauth_service.save_token(user.id, token)

                # Generate JWT token for session
                jwt_token = self.auth_service.create_access_token({"sub": user.username})

                logger.info(f"User {user.username} authenticated successfully with LinkedIn.")

                return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})

            except Exception as e:
                logger.error(f"Error in LinkedIn callback: {e}")
                return HTMLResponse(f"<h1>LinkedIn Authentication Failed</h1><pre>{str(e)}</pre>", status_code=400)
