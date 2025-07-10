from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..services.linkedin_api import LinkedInApiService
import tempfile, shutil, os

router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])
li_service = LinkedInApiService()

@router.post("/post")
async def post_text(text: str = Form(...)):
    try:
        result = await li_service.post_text(text)
        return {"message": "Post published!", "post_urn": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/post-with-image")
async def post_with_image(
    text: str = Form(...),
    image: UploadFile = File(...)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(image.file, tmp)
        tmp_path = tmp.name
    try:
        result = await li_service.post_with_image(text, tmp_path)
        return {"message": "Post with image published!", "post_urn": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(tmp_path)
