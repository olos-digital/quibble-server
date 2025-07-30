from typing import List

from sqlalchemy.orm import Session

from database.models.post_planning import PostPlan, PlannedPost
from schemas.planning import (
	PostPlanCreate,
	PostPlanRead,
	PlannedPostCreate,
	PlannedPostRead,
)
from utilities.mistral_client import MistralClient


class PostPlanningService:
	def __init__(self, db: Session, ai: MistralClient):
		self.db = db
		self.ai = ai


	def create_plan(self, data: PostPlanCreate) -> PostPlanRead:
		# 1. instantiate PostPlan
		plan = PostPlan(
			account_id=data.account_id,
			plan_date=data.plan_date,
			status="draft",
		)
		self.db.add(plan)
		self.db.commit()
		self.db.refresh(plan)

		return PostPlanRead(
			id=plan.id,
			account_id=plan.account_id,
			plan_date=plan.plan_date,
			status=plan.status,
			posts=[],
		)

	def generate_posts(self, plan_id: int) -> List[PlannedPostRead]:
		plan = self.db.query(PostPlan).get(plan_id)
		if not plan:
			raise ValueError(f"Plan {plan_id} not found")

		prompt = (
			f"Generate 5 LinkedIn/Instagram post drafts for "
			f"account {plan.account_id} on {plan.plan_date.date()}"
		)

		drafts = self.ai.generate_posts(prompt, n=5)
		created = []
		for text in drafts:
			pp = PlannedPost(plan_id=plan.id, content=text, ai_suggested=1)
			self.db.add(pp);
			created.append(pp)
		self.db.commit()
		return [PlannedPostRead(
			id=p.id, content=p.content,
			scheduled_time=p.scheduled_time,
			ai_suggested=bool(p.ai_suggested),
		) for p in created]


	def update_post(
			self,
			plan_id: int,
			post_id: int,
			data: PlannedPostCreate,
	) -> PlannedPostRead:
		post = (
			self.db.query(PlannedPost)
			.filter_by(id=post_id, plan_id=plan_id)
			.first()
		)
		if not post:
			raise ValueError(f"Post {post_id} not found in plan {plan_id}")

		post.content = data.content
		post.scheduled_time = data.scheduled_time
		self.db.commit()
		self.db.refresh(post)

		return PlannedPostRead(
			id=post.id,
			content=post.content,
			scheduled_time=post.scheduled_time,
			ai_suggested=bool(post.ai_suggested),
		)
