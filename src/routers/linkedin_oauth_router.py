from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from src.database.models.user import User
from src.oauth.linkedin_token import exchange_authorization_code, get_authorize_url
from src.services.linkedin_oauth_service import LinkedInOAuthService
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.repositories.user_repo import UserRepository
from src.database.db_config import get_db

from src.utilities import logger	
logger = logger.setup_logger("LinkedInOAuthRouter logger")

class LinkedInOAuthRouter:
    def __init__(self, linkedin_oauth_service: LinkedInOAuthService, auth_service: AuthService, user_repo: UserRepository):
        self.router = APIRouter(prefix="/auth/linkedin", tags=["LinkedIn OAuth"])
        self.linkedin_oauth_service = linkedin_oauth_service
        self.auth_service = auth_service
        self.user_repo = user_repo
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/login")
        def linkedin_login(state: str = "randomstring"):
            url = get_authorize_url(state=state)
            logger.info(f"Redirecting to LinkedIn login with url: {url}")
            return RedirectResponse(url)

        @self.router.get("/callback")
        def linkedin_callback(
            code: str,
        ):
            try:
                token = exchange_authorization_code(code)

                # Try to find user by LinkedIn URN; if not found, create user
                user = self.user_repo.get_by_linkedin_urn(token.owner_urn)
                logger.info(f"LinkedIn token received for user: {token.owner_urn}")
                
                if not user:
                    # You can also check by email if you want fetch it from LinkedIn API
                    username = f"li_{token.owner_urn.replace('urn:li:person:', '')}"
                    user = self.user_repo.create(
                        User(username=username, hashed_password=token.access_token) # password is supposed to be changed by user in the future
                    )

                # Update LinkedIn token info in DB via the service
                logger.debug(f"Saving LinkedIn token for user ID: {user.id}")
                self.linkedin_oauth_service.save_token(user.id, token)
                # Generate your system JWT for this user
                jwt_token = self.auth_service.create_access_token({"sub": user.username})
                logger.info(f"User {user.username} authenticated successfully with LinkedIn.")
                return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})

            except Exception as e:
                return HTMLResponse(f"<h1>LinkedIn Auth Failed</h1><pre>{str(e)}</pre>", status_code=400)
