
import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.linkedin_post_service import LinkedInPostService
from src.services.linkedin_oauth_service import LinkedInOAuthService
from src.services.auth_service import AuthService
from src.repositories.user_repo import UserRepository
from src.utilities import logger

logger = logger.setup_logger("LinkedInPostRouter logger")

class LinkedInPostRouter:
    def __init__(self, auth_service: AuthService, user_repo: UserRepository, linkedin_oauth_service: LinkedInOAuthService):
        self.router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])
        self.auth_service = auth_service
        self.user_repo = user_repo
        self.linkedin_oauth_service = linkedin_oauth_service
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/post")
        async def post_text(
            caption: str = Form(...),
            current_user = Depends(self.auth_service.get_current_user)
        ):
            token = self.linkedin_oauth_service.get_token(current_user.id)
            if not token:
                raise HTTPException(403, "No LinkedIn token found. Please authorize first.")
            li_service = LinkedInPostService(token=token)
            urn = await li_service.post_text(caption)
            return {"message": "LinkedIn text post created", "post_urn": urn}

        @self.router.post("/post-with-image")
        async def post_image(
            caption: str = Form(...),
            image: UploadFile = File(...),
            current_user = Depends(self.auth_service.get_current_user)
        ):
            logger.info(f"Current User: {current_user}")
            token = self.linkedin_oauth_service.get_token(current_user.id)
            logger.info(f"LinkedIn token for user {current_user.username}: {token}")
            if not token:
                raise HTTPException(403, "No LinkedIn token found. Please authorize first.")

            li_service = LinkedInPostService(token=token)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                shutil.copyfileobj(image.file, tmp)
                tmp_path = tmp.name

            try:
                urn = await li_service.post_with_image(caption, tmp_path)
                return {"message": "LinkedIn image post created", "post_urn": urn}
            except Exception as e:
                raise HTTPException(status_code=500, detail="LinkedIn API error") from e
            finally:
                os.remove(tmp_path)
