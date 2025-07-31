import os
import time

import requests
from pydantic import BaseModel


class LinkedInToken(BaseModel):
    """
    Pydantic model for LinkedIn OAuth token data.
    
    This model structures the token response for type safety and validation
    in FastAPI applications. It is used to handle access/refresh tokens securely,
    ensuring consistent data handling during authentication and API calls.
    
    Attributes:
        access_token (str): Bearer token for API authentication.
        expires_at (float): Unix timestamp when the token expires.
        owner_urn (str): LinkedIn URN of the token owner (e.g., 'urn:li:person:ID').
        refresh_token (str | None): Optional token for refreshing access (defaults to None).
    """
    access_token: str
    expires_at: float          # epoch seconds
    owner_urn: str
    refresh_token: str | None = None


# Environment variables: Loaded for OAuth configuration
CLIENT_ID     = os.getenv("LI_CLIENT_ID")
CLIENT_SECRET = os.getenv("LI_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("LI_REDIRECT_URI")
TOKEN_URL     = "https://www.linkedin.com/oauth/v2/accessToken"
ME_URL        = "https://api.linkedin.com/v2/userinfo"


def exchange_authorization_code(code: str) -> LinkedInToken:
    """
    Exchanges an authorization code for a LinkedIn access token.
    
    This function handles the OAuth code exchange flow, fetching a fresh token
    and the user's URN. It is designed for FastAPI callback endpoints to securely
    obtain tokens after user consent, enabling subsequent API interactions.
    
    Args:
        code (str): Temporary authorization code from LinkedIn redirect.
    
    Returns:
        LinkedInToken: Parsed token data including access token and URN.
    
    Raises:
        requests.HTTPError: If the token exchange or user info request fails.
    """
    data = dict(
        grant_type    = "authorization_code",
        code          = code,
        redirect_uri  = REDIRECT_URI,
        client_id     = CLIENT_ID,
        client_secret = CLIENT_SECRET,
    )
    resp = requests.post(TOKEN_URL, data=data, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    
    # Fetch user URN: required for ownership in LinkedIn API calls
    me = requests.get(ME_URL,
                      headers={"Authorization": f"Bearer {payload['access_token']}",
                               "X-Restli-Protocol-Version": "2.0.0"},
                      timeout=10).json()
    urn = f"urn:li:person:{me['sub']}"
    
    return LinkedInToken(
        access_token = payload["access_token"],
        refresh_token= payload.get("refresh_token"),
        expires_at   = time.time() + payload["expires_in"],
        owner_urn    = urn,
    )


def refresh_access_token(refresh_token: str) -> LinkedInToken:
    """
    Refreshes an expired LinkedIn access token using a refresh token.
    
    This function is used in long-lived sessions or background tasks within FastAPI
    to maintain access without re-authentication. 
    
    Args:
        refresh_token (str): Valid refresh token from a previous exchange.
    
    Returns:
        LinkedInToken: Updated token data with a new access token.
    
    Raises:
        requests.HTTPError: If the refresh request fails.
    """
    data = dict(
        grant_type    = "refresh_token",
        refresh_token = refresh_token,
        client_id     = CLIENT_ID,
        client_secret = CLIENT_SECRET,
    )
    resp = requests.post(TOKEN_URL, data=data, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    return LinkedInToken(
        access_token = payload["access_token"],
        refresh_token= refresh_token,
        expires_at   = time.time() + payload["expires_in"],
        owner_urn    = "",  # urn is not refetched, assume it's stored elsewhere.
    )
