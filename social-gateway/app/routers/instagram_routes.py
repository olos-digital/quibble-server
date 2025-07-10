# routers/linkedin_routes.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from .deps import get_current_user, get_db
from services.linkedin_api import LinkedInApiService
import tempfile, shutil, os, asyncio

router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])

@router.post("/post")
async def linkedin_post(
    text: str = Form(...),
    image: UploadFile | None = File(None),
    user = Depends(get_current_user),
    db   = Depends(get_db)):
    token = get_token_for_user(db, user, "linkedin")
    if not token:
        raise HTTPException(403, "LinkedIn not authorised")

    li = LinkedInApiService(token)

    if image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            shutil.copyfileobj(image.file, tmp)
            path = tmp.name
        try:
            post_id = await li.post_with_image(text, path)
        finally:
            os.remove(path)
    else:
        post_id = await li.post_text(text)

    return {"message": "Posted to LinkedIn", "post_urn": post_id}
