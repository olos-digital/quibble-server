from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.models.base import Base

class XToken(Base):
    __tablename__ = "x_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)

    access_token = Column(String, nullable=False)        # encrypted
    refresh_token = Column(String, nullable=False)       # encrypted
    expires_at = Column(Float, nullable=True)
    owner_urn = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="x_token")
