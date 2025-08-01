import os

import tweepy


class XApiService:
	"""
	Service class for interacting with the X (Twitter) API in FastAPI.

	This class initializes Tweepy clients for v2 (tweets) and v1 (media uploads),
	loading credentials from environment variables and validating them. It provides
	methods for posting tweets, designed for dependency injection in routes to enable
	social media features with robust error handling for missing configs.
	"""

	def __init__(self):
		# load credentials fetched from .env vars for security; avoids hardcoding sensitive data.
		self.consumer_key = os.getenv("X_CONSUMER_KEY")
		self.consumer_secret = os.getenv("X_CONSUMER_SECRET")
		self.access_token = os.getenv("X_ACCESS_TOKEN")
		self.access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

		# checks for missing vars early to fail fast during initialization.
		missing = [k for k, v in {
			"X_CONSUMER_KEY": self.consumer_key,
			"X_CONSUMER_SECRET": self.consumer_secret,
			"X_ACCESS_TOKEN": self.access_token,
			"X_ACCESS_TOKEN_SECRET": self.access_token_secret,
		}.items() if not v]
		if missing:
			raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

		# Tweepy Client: For v2 API operations like creating tweets.
		self.client = tweepy.Client(
			consumer_key=self.consumer_key,
			consumer_secret=self.consumer_secret,
			access_token=self.access_token,
			access_token_secret=self.access_token_secret
		)
		# OAuth1 Handler required for v1 API (media uploads) due to Twitter's API versioning.
		self.auth = tweepy.OAuth1UserHandler(
			self.consumer_key, self.consumer_secret,
			self.access_token, self.access_token_secret
		)
		self.api_v1 = tweepy.API(self.auth)

	def post_tweet(self, text: str):
		"""
		Posts a simple text tweet to X (Twitter).

		This method uses the Tweepy client to create a tweet, returning the response data
		for further processing (e.g., extracting tweet ID in endpoints).

		Args:
			text (str): The tweet content.

		Returns:
			dict: Response data from the Twitter API.
		"""
		response = self.client.create_tweet(text=text)
		return response.data

	def post_tweet_with_image(self, text: str, image_path: str):
		"""
		Posts a tweet with an attached image to X (Twitter).

		This method first uploads the image via v1 API to get a media ID, then creates
		the tweet with the media attached using v2. It handles the hybrid API usage
		required by Twitter's endpoints for media posts.

		Args:
			text (str): The tweet text.
			image_path (str): Path to the local image file.

		Returns:
			dict: Response data from the Twitter API.
		"""
		# Upload image: Uses v1 API to obtain media ID for attachment.
		media = self.api_v1.media_upload(image_path)
		response = self.client.create_tweet(text=text, media_ids=[media.media_id])
		return response.data
