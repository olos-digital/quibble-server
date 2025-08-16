from src.database.models.x_token import XTokenModel
from src.utilities.token_encryptor import encrypt_token

class XTokenRepository:
    def __init__(self, db_session):
        self.db = db_session

    def get_by_user_id(self, user_id: str) -> XTokenModel:
        return self.db.query(XTokenModel).filter_by(user_id=user_id).first()

    def create_or_update(self, user_id: str, access_token: str, owner_urn: str, expires_at=None) -> XTokenModel:
        token = self.get_by_user_id(user_id)
        if token:
            token.access_token = encrypt_token(access_token)
            token.expires_at = expires_at
            token.owner_urn = owner_urn
        else:
            token = XTokenModel(
                user_id=user_id,
                access_token=encrypt_token(access_token),
                expires_at=expires_at,
                owner_handle=owner_urn
            )
            self.db.add(token)
        self.db.commit()
        return token
