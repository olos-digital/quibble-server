import os
import tweepy
from src.utilities import logger
from src.exceptions.x_exception import XApiException

logger = logger.setup_logger("XApiService logger")


class XApiService:
    """
    Service class for interacting with the X (Twitter) API in FastAPI.

    Handles posting text tweets and tweets with images by bridging Tweepy v2 (text) and v1 (media).
    """

    def __init__(self):
        # Load credentials securely from environment variables
        self.consumer_key = os.getenv("X_CONSUMER_KEY")
        self.consumer_secret = os.getenv("X_CONSUMER_SECRET")
        self.access_token = os.getenv("X_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

        # Fail fast if any env var is missing
        missing = [k for k, v in {
            "X_CONSUMER_KEY": self.consumer_key,
            "X_CONSUMER_SECRET": self.consumer_secret,
            "X_ACCESS_TOKEN": self.access_token,
            "X_ACCESS_TOKEN_SECRET": self.access_token_secret,
        }.items() if not v]
        if missing:
            logger.critical(f"Initialization failed. Missing env vars: {', '.join(missing)}")
            raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

        # Initialize Tweepy v2 client for modern endpoints (e.g. create_tweet)
        self.client = tweepy.Client(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )
        # OAuth1 handler required for v1 (e.g., media uploads)
        self.auth = tweepy.OAuth1UserHandler(
            self.consumer_key, self.consumer_secret,
            self.access_token, self.access_token_secret
        )
        self.api_v1 = tweepy.API(self.auth)

        logger.info("XApiService initialized: Tweepy v2/v1 clients ready.")

    def post_tweet(self, text: str):
        """
        Posts a simple text tweet using the v2 API.

        Args:
            text (str): The tweet content.

        Returns:
            dict: Response data from Twitter API (including tweet ID).
        """
        logger.info(f"Posting simple tweet: '{text[:50]}...'")
        try:
            response = self.client.create_tweet(text=text)
            logger.info("Simple tweet posted successfully.")
            return response.data

        except Exception as e:
            logger.error(f"Failed to post simple tweet: {e}", exc_info=True)
            raise XApiException("Failed to post simple tweet") from e

    def post_tweet_with_image(self, text: str, image_path: str):
        """
        Posts a tweet with an attached image to X (Twitter).
        This method uses v1 API to upload the image (media), then posts the tweet with the media using v2.

        Args:
            text (str): Tweet text.
            image_path (str): File path to the local image.

        Returns:
            dict: Response data from Twitter API (including tweet ID).

        Raises:
            Exception: On upload, authentication, or create failure.
        """
        logger.info(f"Posting tweet with image. Text: '{text[:50]}...', Image path: {image_path}")
        try:
            # Upload image to v1 endpoint to get media ID
            media = self.api_v1.media_upload(image_path)
            logger.debug(f"Media uploaded. Media ID: {media.media_id}")

            # Post tweet with attached media
            response = self.client.create_tweet(text=text, media_ids=[media.media_id])
            logger.info("Tweet with image posted successfully.")
            return response.data

        except Exception as e:
            logger.error(f"Failed to post tweet with image: {e}", exc_info=True)
            raise XApiException("Failed to post tweet with image") from e