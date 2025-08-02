import os
import shutil
import tempfile

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from src.services.x_service import XApiService
from src.utilities import logger

logger = logger = logger.setup_logger("XRouter logger")

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
		def post_simple_tweet(text: str = Form(...)) -> dict:
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
				HTTPException: Returns 400 status with error detail on failure.
			"""
			logger.info(f"Received request to post simple tweet: {text[:50]}...")

			try:
				result = x_service.post_tweet(text)
				tweet_id = result.get("id")
				logger.info(f"Tweet posted successfully with ID: {tweet_id}")
				return {"message": "Tweet posted!", "tweet_id": tweet_id}
			
			except Exception as e:
				logger.error(f"Failed to post tweet: {e}", exc_info=True)
				raise HTTPException(status_code=400, detail=str(e))

		@self.router.post("/tweet-with-image")
		def post_tweet_with_image(
				text: str = Form(...),  # form field for tweet text.
				image: UploadFile = File(...)  # image file upload.
		) -> dict:
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
                HTTPException: Returns 400 status with error detail on failure.

            Note:
                The temporary file is always removed after the request handling,
                even if an exception occurs, preventing disk clutter.
            """
			tmp_path = None
			logger.info(f"Received request to post tweet with image: '{text[:50]}...' Filename: {image.filename}")

			try:
				# Create a temp file to save the uploaded image
				with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
					shutil.copyfileobj(image.file, tmp)
					tmp_path = tmp.name
					logger.debug(f"Saved uploaded image temporarily at {tmp_path}")

				result = x_service.post_tweet_with_image(text, tmp_path)
				tweet_id = result.get("id")
				logger.info(f"Tweet with image posted successfully, ID: {tweet_id}")
				return {"message": "Tweet with image posted!", "tweet_id": tweet_id}

			except Exception as e:
				logger.error(f"Failed to post tweet with image: {e}", exc_info=True)
				raise HTTPException(status_code=400, detail=str(e))

			finally:
				# Cleanup: delete temp file safely if it was created
				if tmp_path:
					try:
						os.remove(tmp_path)
						logger.debug(f"Temporary file {tmp_path} removed successfully.")
					
					except Exception as cleanup_error:
						logger.error(f"Error removing temporary file {tmp_path}: {cleanup_error}", exc_info=True)


# Export router: allows inclusion in the main app via app.include_router(x_router).
x_router = XRouter().router
