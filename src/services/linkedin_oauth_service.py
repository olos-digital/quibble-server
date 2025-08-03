# src/services/linkedin_oauth_service.py

from src.repositories.user_repo import UserRepository
from src.oauth.linkedin_token import LinkedInToken

class LinkedInOAuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def save_token(self, user_id: int, token: LinkedInToken):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.li_access_token = token.access_token
        user.li_refresh_token = token.refresh_token
        user.li_expires_at = token.expires_at
        user.li_owner_urn = token.owner_urn
        self.user_repo.update(user)
    
    def get_token(self, user_id: int) -> LinkedInToken | None:
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.li_access_token:
            return None
        return LinkedInToken(
            access_token=user.li_access_token,
            refresh_token=user.li_refresh_token,
            expires_at=user.li_expires_at,
            owner_urn=user.li_owner_urn,
        )
