import os, requests, time, httpx, types

class LinkedInApiService:
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE  = "https://api.linkedin.com/rest"


    def __init__(self, user_token: object | None = None) -> None:
        if user_token is None:
            self.token = types.SimpleNamespace(
                access_token = os.getenv("LI_ACCESS_TOKEN"),
                refresh_token= os.getenv("LI_REFRESH_TOKEN"),
                expires_at   = float(os.getenv("LI_ACCESS_TOKEN_EXPIRES", "0")),
                owner_urn    = os.getenv("LI_OWNER_URN"),
                save         = lambda: None
            )
        else:
            self.token = user_token

    def _auth_header(self):
        if self.token.expires_at <= time.time():
            self._refresh_token()
        return {"Authorization": f"Bearer {self.token.access_token}",
                "LinkedIn-Version": "202506",     # required header
                "X-Restli-Protocol-Version": "2.0.0"}

    def _refresh_token(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.token.refresh_token,
            "client_id": os.getenv("LI_CLIENT_ID"),
            "client_secret": os.getenv("LI_CLIENT_SECRET")
        }
        r = requests.post(self.TOKEN_URL, data=data, timeout=10)
        r.raise_for_status()
        payload = r.json()
        self.token.access_token = payload["access_token"]
        self.token.expires_at   = time.time() + payload["expires_in"]
        self.token.save()

    async def post_text(self, text: str):
        body = {
            "author": self.token.owner_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "lifecycleState": "PUBLISHED",
            "distribution": {"feedDistribution": "MAIN_FEED"}
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.API_BASE}/posts",
                                  headers=self._auth_header(),
                                  json=body, timeout=15)
            r.raise_for_status()
            return r.headers["x-linkedin-id"]      # post URN

    async def post_with_image(self, text: str, img_path: str):
        # register upload
        reg_body = {
          "registerUploadRequest": {
             "owner": self.token.owner_urn,
             "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
             "serviceRelationships":[{"relationshipType":"OWNER",
                                       "identifier":"urn:li:userGeneratedContent"}]
          }
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.API_BASE}/assets?action=registerUpload",
                                  headers=self._auth_header(), json=reg_body)
            r.raise_for_status()
            data = r.json()["value"]
            asset  = data["asset"]
            upload = data["uploadMechanism"]["com.linkedin.digitalmedia."
                                            "uploading.MediaUploadHttpRequest"]["uploadUrl"]

        # upload binary
        with open(img_path, "rb") as fp:
            httpx.put(upload, headers={"Authorization": f"Bearer {self.token.access_token}",
                                       "Content-Type": "image/jpeg"}, data=fp.read())

        # create post
        body = {
            "author": self.token.owner_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "lifecycleState": "PUBLISHED",
            "distribution": {"feedDistribution": "MAIN_FEED"},
            "content": {"media": {"id": asset}}
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.API_BASE}/posts",
                                  headers=self._auth_header(), json=body)
            r.raise_for_status()
            return r.headers["x-linkedin-id"]
