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

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/x", tags=["X (Twitter)"])
        self._x_service = XApiService()

        self._setup_routes()

    def _setup_routes(self) -> None:
        x_service = self._x_service  # local alias for the closures below

        @self.router.post("/tweet")
        def post_simple_tweet(text: str = Form(...)):
            try:
                result = x_service.post_tweet(text)
                return {"message": "Tweet posted!", "tweet_id": result.get("id")}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.post("/tweet-with-image")
        def post_tweet_with_image(
            text: str = Form(...),
            image: UploadFile = File(...)
        ):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                shutil.copyfileobj(image.file, tmp)
                tmp_path = tmp.name
            try:
                result = x_service.post_tweet_with_image(text, tmp_path)
                return {"message": "Tweet with image posted!", "tweet_id": result.get("id")}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
            finally:
                os.remove(tmp_path)

x_router = XRouter().router
