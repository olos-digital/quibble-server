from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
)
import tempfile
import shutil
import os

from services.linkedin_service import LinkedInApiService
from utilities.linkedin_helper import get_linkedin_token

class LinkedInRouter: 
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])
        self._setup_routes()

    def _setup_routes(self) -> None:
        @self.router.post("/post")
        async def post_text(
            caption: str = Form(...),
            token = Depends(get_linkedin_token)
        ):
            urn = await LinkedInApiService(token).post_text(caption)
            return {"message": "LinkedIn text post created", "post_urn": urn}

        @self.router.post("/post-with-image")
        async def post_image(
            caption: str = Form(...),
            image: UploadFile = File(...),
            token = Depends(get_linkedin_token)
        ):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                shutil.copyfileobj(image.file, tmp)
                tmp_path = tmp.name
            try:
                urn = await LinkedInApiService(token).post_with_image(caption, tmp_path)
                return {"message": "LinkedIn image post created", "post_urn": urn}
            finally:
                os.remove(tmp_path)

linkedin_router = LinkedInRouter().router
