from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..services.x_api import XApiService
import tempfile
import shutil
import os

router = APIRouter(prefix="/x", tags=["X (Twitter)"])
x_service = XApiService()

@router.post("/tweet")
def post_simple_tweet(text: str = Form(...)):
    try:
        result = x_service.post_tweet(text)
        return {"message": "Tweet posted!", "tweet_id": result.get("id")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tweet-with-image")
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
