import os
import shutil
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query

from src.database.models import user
from src.schemas import post_schemas
from src.services.auth_service import AuthService
from src.services.post_service import PostService


def get_uploads_dir() -> str:
	return os.getenv("UPLOADS_DIR", "uploads")


class PostRouter:
	"""
	Router for post management: listing, retrieval, deletion, image upload, and
	user-specific post fetches. Accepts an AuthService and a PostService instance
	(typically injected in tests or via DI container).
	"""

	def __init__(self, auth_service: AuthService, post_service: PostService):
		self.router = APIRouter()
		self.auth_service = auth_service
		self.post_service = post_service  # use this everywhere
		self._setup_routes()

	def _setup_routes(self):
		@self.router.get("/me", response_model=list[post_schemas.Post])
		def get_my_posts(
				current_user: user.User = Depends(self.auth_service.get_current_user),
		):
			return self.post_service.get_user_posts(current_user)

		@self.router.get("/", response_model=list[post_schemas.Post])
		def list_posts(
				category: Optional[str] = Query(None, description="Filter by category"),
				sort_by: Optional[str] = Query("likes", description="Sorting: 'likes' or 'newest'"),
		):
			return self.post_service.get_posts(category=category, sort_by=sort_by)

		@self.router.get("/{post_id}", response_model=post_schemas.Post)
		def get_post_by_id(
				post_id: int,
		):
			post_obj = self.post_service.get_post(post_id)
			if not post_obj:
				raise HTTPException(status_code=404, detail="Post not found")
			return post_obj

		@self.router.delete("/{post_id}")
		def delete_post(
				post_id: int,
				current_user: user.User = Depends(self.auth_service.get_current_user),
		):
			success = self.post_service.delete_post(current_user, post_id)
			if not success:
				raise HTTPException(status_code=403, detail="Not allowed or post not found")
			return {"message": "Deleted"}

		@self.router.post("/{post_id}/image", response_model=post_schemas.Post)
		def upload_post_image(
				post_id: int,
				image: UploadFile = File(...),
				current_user: user.User = Depends(self.auth_service.get_current_user),
		):
			uploads_dir = get_uploads_dir()
			os.makedirs(uploads_dir, exist_ok=True)
			filename = f"{uuid.uuid4().hex}_{image.filename}"
			filepath = os.path.join(uploads_dir, filename)

			try:
				with open(filepath, "wb") as buffer:
					shutil.copyfileobj(image.file, buffer)
				image_url = f"/{uploads_dir}/{filename}"
				updated = self.post_service.update_post_image(current_user, post_id, image_url)
				if not updated:
					raise HTTPException(status_code=403, detail="Not allowed or post not found")
				return updated
			finally:
				image.file.close()
