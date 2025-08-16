import os
import time

import requests
from pydantic import BaseModel

from src.utilities import logger

logger = logger.setup_logger("LinkedInToken logger")

class LinkedInToken(BaseModel):
	"""
	Pydantic model for LinkedIn OAuth token data.

	This model structures the token response for type safety and validation
	in FastAPI applications. It is used to handle access/refresh tokens securely,
	ensuring consistent data handling during authentication and API calls.
	"""
	access_token: str
	refresh_token: str | None = None
	expires_at: float
	owner_urn: str


# Environment variables: Loaded for OAuth configuration
CLIENT_ID = os.getenv("LI_CLIENT_ID")
CLIENT_SECRET = os.getenv("LI_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LI_REDIRECT_URI")
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
ME_URL = "https://api.linkedin.com/v2/userinfo" 


def get_authorize_url(state: str):
	from urllib.parse import urlencode
	base = "https://www.linkedin.com/oauth/v2/authorization"
	params = dict(
		response_type="code",
		client_id=CLIENT_ID,
		redirect_uri=REDIRECT_URI,
		scope="openid profile email",
		state=state
	)
	logger.debug(f"Generating LinkedIn OIDC authorization URL with params: {params}")
	return f"{base}?{urlencode(params)}"

def exchange_authorization_code(code: str, 
								user_id: int,
								linkedin_token_repo) -> LinkedInToken:
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
		grant_type="authorization_code",
		code=code,
		redirect_uri=REDIRECT_URI,
		client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
	)
	resp = requests.post(TOKEN_URL, data=data, timeout=20)
	resp.raise_for_status()
	payload = resp.json()

	logger.info(f"Authorisation payload: {payload}")

	# Fetch user URN: required for ownership in LinkedIn API calls
	refresh_token = payload.get("refresh_token")

	# Fetch user info
	me = requests.get(
		ME_URL,
		headers={"Authorization": f"Bearer {payload['access_token']}"},
		timeout=10
	).json()
	logger.info(f"User info: {me}")

	owner_urn = f"oidc:linkedin:{me['sub']}"

	token_obj = LinkedInToken(
		access_token=payload["access_token"],
		refresh_token=refresh_token,
		expires_at=time.time() + payload["expires_in"],
		owner_urn=owner_urn,
	)

	# Store token in DB using the repository
	try:
		linkedin_token_repo.save_token(token_obj, user_id=user_id)
		logger.info("Access token saved to DB.")
	except Exception as e:
		logger.error(f"Failed to save access token: {e}")

	return token_obj


def refresh_token_if_needed(token: LinkedInToken) -> LinkedInToken:
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
	# Refresh only if refresh token exists and access token expires in less than 60s
	if token.refresh_token and token.expires_at - time.time() < 60:
		logger.info("Refreshing LinkedIn access token...")
		data = {
			"grant_type": "refresh_token",
			"refresh_token": token.refresh_token,
			"client_id": CLIENT_ID,
			"client_secret": CLIENT_SECRET,
		}
		resp = requests.post(TOKEN_URL, data=data)
		resp.raise_for_status()
		payload = resp.json()
		logger.info(f"Refreshed token payload: {payload}")

		# Update token fields
		token.access_token = payload["access_token"]
		token.expires_at = time.time() + payload["expires_in"]

		# Some flows may rotate refresh token too
		if "refresh_token" in payload:
			token.refresh_token = payload["refresh_token"]

	return token