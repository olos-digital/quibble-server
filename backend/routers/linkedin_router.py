from fastapi import APIRouter, UploadFile, File, Form
import os, uuid, shutil
from services.linkedin_service import LinkedInService

class LinkedInPostRouter:
    def __init__(self, linkedin_service: LinkedInService):
        self.router = APIRouter()
        self.linkedin_service = linkedin_service
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/linkedin_post")
        def linkedin_post(text: str = Form(...), image: UploadFile = File(...)):
            os.makedirs("temp_uploads", exist_ok=True)
            filename = f"temp_{uuid.uuid4().hex}_{image.filename}"
            filepath = os.path.join("temp_uploads", filename)

            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            try:
                self.linkedin_service.publish_post(text, filepath)
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)

            return {"message": "Post uploaded to LinkedIn"}