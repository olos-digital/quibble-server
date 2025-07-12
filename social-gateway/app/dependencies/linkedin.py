
import time
from fastapi import Depends, HTTPException

from ..oauth.linkedin_oauth import LinkedInToken, refresh_access_token
from ..dependencies.auth import get_current_user, User
from ..utilities.token_store import get_token, save_token   # in-memory cache


def get_linkedin_token(
    current_user: User = Depends(get_current_user)
) -> LinkedInToken:
    token: LinkedInToken | None = get_token(current_user.id)
    if token is None:
        raise HTTPException(403, "Connect LinkedIn first")

    # silent refresh when the token is close to expiry
    if token.refresh_token and token.expires_at <= time.time() + 60:
        fresh = refresh_access_token(token.refresh_token)
        fresh.owner_urn = token.owner_urn          # URN never changes
        save_token(current_user.id, fresh)         # overwrite cache
        token = fresh

    return token
