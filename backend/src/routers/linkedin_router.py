import os
import shutil
import tempfile

from fastapi import (
	APIRouter,
	UploadFile,
	File,
	Form,
	Depends,
)
from services.linkedin_service import LinkedInApiService  # Service for LinkedIn API interactions.
from utilities.linkedin_helper import get_linkedin_token


class LinkedInRouter:
    """
    Router class for LinkedIn integration endpoints in FastAPI.
    
    This class defines routes for posting text and images to LinkedIn, using dependency
    injection for tokens and handling temporary file uploads securely. It is supposed to
    ensure reliable social media posting with minimal resource leaks.
    """
    
    def __init__(self) -> None:
        # sets prefix and tags for OpenAPI grouping; no additional params needed.
        self.router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])
        self._setup_routes()  # Internal method to configure routes.

    def _setup_routes(self) -> None:
        # defines async handlers; kept private for encapsulation.
        
        @self.router.post("/post")
        async def post_text(
            caption: str = Form(...),
            token=Depends(get_linkedin_token)  # injected LinkedIn token via dependency.
        ):
            """
            Creates a text post on LinkedIn.
            
            This async endpoint uses the injected token to post a caption via the service,
            returning the post URN. It leverages FastAPI's async capabilities for non-blocking
            I/O, suitable for external API calls, and includes basic error propagation.
            
            Args:
                caption (str): Text content for the LinkedIn post.
                token: Auth token from dependency (e.g., from user session).
            
            Returns:
                dict: Success message and post URN.
            """
            urn = await LinkedInApiService(token).post_text(caption)
            return {"message": "LinkedIn text post created", "post_urn": urn}
        
        @self.router.post("/post-with-image")
        async def post_image(
            caption: str = Form(...),  
            image: UploadFile = File(...),
            token=Depends(get_linkedin_token)  
        ):
            """
            Creates an image post on LinkedIn.
            
            This async endpoint handles file uploads by saving to a temporary file,
            posting via the service, and ensuring cleanup in a finally block. It uses async for efficiency
            and raising exceptions for errors like invalid tokens or API failures.
            
            Args:
                caption (str): Text caption for the image post.
                image (UploadFile): Uploaded image file.
                token: Auth token from dependency.
            
            Returns:
                dict: Success message and post URN.
            
            Note: Temp file is always removed to prevent disk clutter; consider async file I/O for very large files.
            """
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                shutil.copyfileobj(image.file, tmp)
                tmp_path = tmp.name
            try:
                urn = await LinkedInApiService(token).post_with_image(caption, tmp_path)
                return {"message": "LinkedIn image post created", "post_urn": urn}
            finally:
                os.remove(tmp_path)

linkedin_router = LinkedInRouter().router
