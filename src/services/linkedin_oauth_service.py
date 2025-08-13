from src.repositories.user_repo import UserRepository
from src.oauth.linkedin_token import LinkedInToken
from src.utilities.token_encryptor import decrypt_token, encrypt_token

class LinkedInOAuthService:
    """
    Service class for handling LinkedIn OAuth token storage and retrieval.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def save_token(self, user_id, token: LinkedInToken):
        """
        Encrypts and saves the LinkedIn OAuth token for a user.

        Args:
            user_id: The unique identifier of the user.
            token (LinkedInToken): The LinkedIn token object containing access and refresh tokens.
        """
        self.repo.create_or_update(
            user_id,
            encrypt_token(token.access_token),
            encrypt_token(token.refresh_token) if token.refresh_token else None,
            token.owner_urn,
            token.expires_at
        )
    
    def get_token(self, user_id) -> LinkedInToken | None:
        """
        Retrieves and decrypts the LinkedIn OAuth token for a user.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            LinkedInToken | None: The LinkedIn token object if found, otherwise None.
        """
        record = self.repo.get_by_user_id(user_id)
        if not record:
            return None
        return LinkedInToken(
            access_token=decrypt_token(record.access_token),
            refresh_token=decrypt_token(record.refresh_token) if record.refresh_token else None,
            expires_at=record.expires_at,
            owner_urn=record.owner_urn
        )
