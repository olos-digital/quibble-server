from src.database.models.linkedin_token import LinkedInToken as LinkedInTokenModel
from src.oauth.linkedin_token import LinkedInToken
from src.utilities.token_encryptor import encrypt_token

class LinkedInTokenRepository:
    def __init__(self, db_session):
        self.db = db_session

    def get_by_user_id(self, user_id: str) -> LinkedInTokenModel:
        return self.db.query(LinkedInTokenModel).filter_by(user_id=user_id).first()

    def create_or_update(self, user_id: str, access_token: str, owner_urn: str, expires_at=None) -> LinkedInTokenModel:
        token = self.get_by_user_id(user_id)
        if token:
            token.access_token = encrypt_token(access_token)
            token.expires_at = expires_at
            token.owner_urn = owner_urn
        else:
            token = LinkedInTokenModel(
                user_id=user_id,
                access_token=encrypt_token(access_token),
                expires_at=expires_at,
                owner_urn=owner_urn
            )
            self.db.add(token)
        self.db.commit()
        return token
    
    def save_token(self, token: LinkedInToken, user_id: str) -> LinkedInTokenModel:
        """
        Saves the LinkedIn token to the database.

        Args:
            token (LinkedInTokenModel): The LinkedIn token object to save.
        """
        tokenModel = LinkedInTokenModel(
            user_id=user_id,
            access_token=encrypt_token(token.access_token),
            expires_at=token.expires_at,
            owner_urn=token.owner_urn
        )
        self.db.add(tokenModel)
        self.db.commit()
        return tokenModel