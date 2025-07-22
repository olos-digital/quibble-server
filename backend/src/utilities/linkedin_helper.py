import time

from fastapi import Depends, HTTPException

from database.models.user import User
from oauth.linkedin_oauth import LinkedInToken, refresh_access_token
from services.auth_service import AuthService
from .token_store import get_token, save_token   # in-memory cache


def get_linkedin_token(
    current_user: User = Depends(AuthService.get_current_user)
) -> LinkedInToken:
    """
    Dependency function to retrieve or refresh a LinkedIn token for the current user.
    
    This FastAPI dependency fetches a cached token, refreshes it if near expiry (using
    the refresh token), and updates the cache.
    
    Args:
        current_user (User): Injected authenticated user from AuthService.
    
    Returns:
        LinkedInToken: Valid (possibly refreshed) token for the user.
    
    Raises:
        HTTPException: 403 if no token is connected for the user.
    """
    token: LinkedInToken | None = get_token(current_user.id)
    if token is None:
        raise HTTPException(403, "Connect LinkedIn first")
    
    # renew if within 60 seconds of expiry to avoid failures.
    if token.refresh_token and token.expires_at <= time.time() + 60:
        fresh = refresh_access_token(token.refresh_token)
        fresh.owner_urn = token.owner_urn  # URN never changes; preserve from original.
        save_token(current_user.id, fresh)
        token = fresh
    
    return token
