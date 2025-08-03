from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .base import Base


class PostPlan(Base):
	__tablename__ = "post_plans"
	id = Column(Integer, primary_key=True, index=True)
	account_id = Column(Integer, nullable=False)
	plan_date = Column(DateTime, nullable=False, index=True)
	status = Column(Enum("draft", "scheduled", "published", name="plan_status"), default="draft")

	posts = relationship("PlannedPost", back_populates="plan")


class PlannedPost(Base):
    __tablename__ = "planned_posts"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("post_plans.id"), nullable=False)
    content = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=True)
    ai_suggested = Column(Integer, default=0)
    image_url = Column(String, nullable=True)

    plan = relationship("PostPlan", back_populates="posts")
