from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from src.oauth.linkedin_oauth import exchange_authorization_code
from src.services.user_service import get_current_user, User
from src.utilities.token_store import save_token

# Defines a dedicated router for callback endpoints to keep the main app clean.
router = APIRouter()


@router.get("/linkedin/callback")
def linkedin_callback(
    code: str,  # Authorization code from LinkedIn's redirect.
    state: str,  # CSRF protection state parameter (should be validated in production).
    current_user: User = Depends(get_current_user),  # Injected current user for associating the token.
):
    """
    Handles the LinkedIn OAuth callback.
    
    This endpoint processes the authorization code from LinkedIn, exchanges it for
    an access token, stores the token associated with the current user, and redirects
    to a dashboard.
    
    Args:
        code (str): Temporary authorization code from LinkedIn.
        state (str): State parameter for CSRF validation (not validated here; add checks in prod).
        current_user (User): Authenticated user via dependency injection.
    
    Returns:
        RedirectResponse: Redirects to the dashboard with a success query parameter.
    
    Note: In production, validate the 'state' parameter to prevent CSRF attacks.
    """
    # cache the token in RAM instead of persisting to the DB for ephemeral storage.
    token = exchange_authorization_code(code)   
    save_token(current_user.id, token)                 

    return RedirectResponse("/dashboard?linkedin=ok")
