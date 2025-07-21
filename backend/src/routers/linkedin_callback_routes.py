from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from services.user_service import get_current_user, User          # your auth util
from ..oauth.linkedin_oauth import exchange_authorization_code
from ..utilities.token_store import save_token

router = APIRouter()

@router.get("/linkedin/callback")
def linkedin_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_user),
):
    # cache the token in RAM instead of persisting to the DB.

    token = exchange_authorization_code(code)   
    save_token(current_user.id, token)                 

    return RedirectResponse("/dashboard?linkedin=ok")
