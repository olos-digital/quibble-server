from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.models.base import Base

class LinkedInToken(Base):
    __tablename__ = "linkedin_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)

    access_token = Column(String, nullable=False)   # encrypted
    refresh_token = Column(String, nullable=True)   # encrypted
    expires_at = Column(Float, nullable=False)      # epoch timestamp
    owner_urn = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="linkedin_token")