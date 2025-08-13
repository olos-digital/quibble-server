from src.oauth.x_token import XToken
from src.utilities.token_encryptor import decrypt_token, encrypt_token


class XTokenService:
    def __init__(self, repo):
        self.repo = repo

    def save_token(self, user_id: str, access: str, refresh: str, owner_urn: str, expires=None):
        self.repo.create_or_update(
            user_id,
            encrypt_token(access),
            encrypt_token(refresh),
            owner_urn,
            expires
        )

    def get_token(self, user_id: str) -> dict | None:
        rec = self.repo.get_by_user_id(user_id)
        if not rec:
            return None
        return XToken(
            access_token=decrypt_token(rec.access_token),
            refresh_token=decrypt_token(rec.refresh_token) if rec.refresh_token else None,
            expires_at=rec.expires_at,
            owner_urn=rec.owner_urn
        )
