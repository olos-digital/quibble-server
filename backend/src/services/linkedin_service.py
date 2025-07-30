import os
import time

import httpx
import requests

from typing import Optional

from oauth.linkedin_oauth import LinkedInToken


class LinkedInApiService:
    """
    Service class for interacting with the LinkedIn API in FastAPI.
    
    This class manages token refresh and API calls (e.g., posting with images),
    using async HTTP for non-blocking operations.
    
    Args:
        token (LinkedInToken): Auth token for API requests.
        client_id (str): LinkedIn app client ID (defaults from .env).
        client_secret (str): LinkedIn app client secret (defaults from .env).
    """
    
    def __init__(
        self,
        token: LinkedInToken,
        client_id: str = os.getenv("LI_CLIENT_ID"),
        client_secret: str = os.getenv("LI_CLIENT_SECRET"),
    ):
        self.token = token
        self.client_id  = client_id
        self.client_secret = client_secret
    
    # API endpoints; kept class-level for easy overriding if needed.
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE  = "https://api.linkedin.com/rest"
    
    async def _ensure_fresh(self):
        """
        Ensures the access token is fresh by refreshing if near expiry.
        
        This internal async method checks and renews the token proactively (within 60s of expiry)
        using the refresh token, updating the instance's token state. It supports non-blocking
        calls in FastAPI async routes to prevent expired token errors during API interactions.
        """
        if (self.token.refresh_token and
            self.token.expires_at <= time.time() + 60):
            data = {
                "grant_type":    "refresh_token",
                "refresh_token": self.token.refresh_token,
                "client_id":     self.client_id,
                "client_secret": self.client_secret,
            }
            r = requests.post(self.TOKEN_URL, data=data, timeout=15)
            r.raise_for_status()
            p = r.json()
            self.token.access_token = p["access_token"]
            self.token.expires_at   = time.time() + p["expires_in"]
    
    def _hdr(self):
        """
        Returns headers for LinkedIn API requests.
        
        This helper generates authentication headers with the current token and
        required protocol versions, ensuring consistent request formatting.
        
        Returns:
            dict: Headers dictionary for API calls.
        """
        return {
            "Authorization": f"Bearer {self.token.access_token}",
            "LinkedIn-Version": "202506",
            "X-Restli-Protocol-Version": "2.0.0",
        }
    
    async def post_with_image(self, caption: str, img_path: str) -> str:
        """
        Posts content with an image to LinkedIn asynchronously.
        
        This method handles the full flow: token refresh, image upload registration,
        binary upload, and post publication. It uses async HTTP for efficiency in
        FastAPI, raising exceptions on failures and returning the post URN for reference.
        
        Args:
            caption (str): Text caption for the post.
            img_path (str): Local path to the image file.
        
        Returns:
            str: URN of the created post.
        
        Raises:
            requests.HTTPError: On API request failures (e.g., invalid token, upload errors).
        """
        await self._ensure_fresh()  # Ensure token is valid before proceeding.
        async with httpx.AsyncClient() as client:
            # Register upload: Prepares LinkedIn for the image asset.
            reg = await client.post(
                f"{self.API_BASE}/assets?action=registerUpload",
                headers=self._hdr(),
                json={
                    "registerUploadRequest": {
                        "owner": self.token.owner_urn,
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "serviceRelationships": [{
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"}]
                    }
                }
            )
            reg.raise_for_status()
            val   = reg.json()["value"]
            asset = val["asset"]
            url   = val["uploadMechanism"]["com.linkedin.digitalmedia."
                           "uploading.MediaUploadHttpRequest"]["uploadUrl"]
            
            # streams the image file to LinkedIn's upload URL.
            with open(img_path, "rb") as fh:
                await client.put(url, content=fh.read(),
                                 headers={"Content-Type": "image/jpeg"})
            
            # creates the post with the uploaded asset and caption.
            pub = await client.post(
                f"{self.API_BASE}/posts",
                headers=self._hdr(),
                json={
                    "author":      self.token.owner_urn,
                    "commentary":  caption,
                    "visibility":  "PUBLIC",
                    "lifecycleState": "PUBLISHED",
                    "distribution":   {"feedDistribution": "MAIN_FEED"},
                    "content": {"media": {"id": asset}}
                }
            )
            pub.raise_for_status()
            return pub.headers["x-linkedin-id"]  # post URN for reference or linking.
