import os
import time, httpx, requests
from typing import Optional
from ..oauth.linkedin_oauth import LinkedInToken


class LinkedInApiService:
    def __init__(
        self,
        token: LinkedInToken,
        client_id: str = os.getenv("LI_CLIENT_ID"),
        client_secret: str = os.getenv("LI_CLIENT_SECRET"),
    ):
        self.token = token
        self.client_id  = client_id
        self.client_secret = client_secret

    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE  = "https://api.linkedin.com/rest"

    async def _ensure_fresh(self):
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
        return {
            "Authorization": f"Bearer {self.token.access_token}",
            "LinkedIn-Version": "202506",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    async def post_with_image(self, caption: str, img_path: str) -> str:
        await self._ensure_fresh()
        async with httpx.AsyncClient() as client:
            # register upload
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

            # binary upload
            with open(img_path, "rb") as fh:
                await client.put(url, content=fh.read(),
                                 headers={"Content-Type": "image/jpeg"})

            #  publish
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
            return pub.headers["x-linkedin-id"]  # post URN
