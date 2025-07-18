import tweepy
import os

class XApiService:
    def __init__(self):
        self.consumer_key = os.getenv("X_CONSUMER_KEY")
        self.consumer_secret = os.getenv("X_CONSUMER_SECRET")
        self.access_token = os.getenv("X_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

        missing = [k for k, v in {
            "X_CONSUMER_KEY": self.consumer_key,
            "X_CONSUMER_SECRET": self.consumer_secret,
            "X_ACCESS_TOKEN": self.access_token,
            "X_ACCESS_TOKEN_SECRET": self.access_token_secret,
        }.items() if not v]
        if missing:                     
            raise RuntimeError(f"Missing env vars: {', '.join(missing)}")
        
        self.client = tweepy.Client(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )
        # for media uploads
        self.auth = tweepy.OAuth1UserHandler(
            self.consumer_key, self.consumer_secret,
            self.access_token, self.access_token_secret
        )
        self.api_v1 = tweepy.API(self.auth)

    def post_tweet(self, text: str):
        response = self.client.create_tweet(text=text)
        return response.data

    def post_tweet_with_image(self, text: str, image_path: str):
        # upload image using, post tweet with media_id
        media = self.api_v1.media_upload(image_path)
        response = self.client.create_tweet(text=text, media_ids=[media.media_id])
        return response.data
