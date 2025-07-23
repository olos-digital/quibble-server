from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
)
import tempfile
import shutil
import os

from services.x_service import XApiService 


class XRouter:
    """
    Router class for X (Twitter) integration endpoints in FastAPI.
    
    This class defines routes for posting text tweets and tweets with images, initializing
    a shared XApiService instance for API calls.
    """
    
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/x", tags=["X (Twitter)"])
        self._x_service = XApiService()
        
        self._setup_routes()  # Internal method to configure routes.

    def _setup_routes(self) -> None:
        # defines handlers; uses a local alias for the shared service.
        x_service = self._x_service  # local alias for the closures below
        
        @self.router.post("/tweet")
        def post_simple_tweet(text: str = Form(...)):
            """
            Posts a simple text tweet to X (Twitter).
            
            This endpoint uses the service to create a tweet, handling exceptions
            gracefully with HTTP responses. It aligns with FastAPI's form data handling
            for straightforward, validated inputs.
            
            Args:
                text (str): The tweet content.
            
            Returns:
                dict: Success message and tweet ID.
            
            Raises:
                HTTPException: 400 on any posting error.
            """
            try:
                result = x_service.post_tweet(text)
                return {"message": "Tweet posted!", "tweet_id": result.get("id")}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.router.post("/tweet-with-image")
        def post_tweet_with_image(
            text: str = Form(...),  # form field for tweet text.
            image: UploadFile = File(...)  # image file upload.
        ):
            """
            Posts a tweet with an attached image to X (Twitter).
            
            This endpoint handles file uploads by saving to a temporary file,
            posting via the service, and ensuring cleanup in a finally block.
            
            Args:
                text (str): The tweet text.
                image (UploadFile): Uploaded image file.
            
            Returns:
                dict: Success message and tweet ID.
            
            Raises:
                HTTPException: 400 on any posting error.
            
            Note: Temp file is always removed to prevent disk clutter.
            """
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                shutil.copyfileobj(image.file, tmp)
                tmp_path = tmp.name
            try:
                result = x_service.post_tweet_with_image(text, tmp_path)
                return {"message": "Tweet with image posted!", "tweet_id": result.get("id")}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
            finally:
                os.remove(tmp_path)  # Ensure temp file cleanup, even on exceptions.


# Export router: allows inclusion in the main app via app.include_router(x_router).
x_router = XRouter().router
