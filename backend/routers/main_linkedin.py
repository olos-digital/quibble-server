from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.upload_image_and_post import publish_post_to_linkedin
import os
import uuid
import shutil

router = APIRouter()

@router.post("/linkedin_post")
def linkedin_post(
    text: str = Form(...),
    image: UploadFile = File(...),
):
    os.makedirs("temp_uploads", exist_ok=True)
    filename = f"temp_{uuid.uuid4().hex}_{image.filename}"
    filepath = os.path.join("temp_uploads", filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    try:
        publish_post_to_linkedin(text=text, image_path=filepath)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    return {"message": "post uploaded to LinkedIn"}