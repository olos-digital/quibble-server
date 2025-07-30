from typing import List
from src.repositories.post_plan_repo import PostPlanRepo
from src.repositories.planned_post_repo import PlannedPostRepo
from src.schemas.planning import (
    PostPlanCreate,
    PostPlanRead,
    PlannedPostCreate,
    PlannedPostRead,
)
from src.utilities.mistral_client import MistralClient


class PostPlanningService:
    def __init__(
        self,
        plan_repo: PostPlanRepo,
        post_repo: PlannedPostRepo,
        ai_client: MistralClient,
    ):
        self.plan_repo = plan_repo
        self.post_repo = post_repo
        self.ai_client = ai_client

    def create_plan(self, data: PostPlanCreate) -> PostPlanRead:
        plan = self.plan_repo.create(data)
        return PostPlanRead(
            id=plan.id,
            account_id=plan.account_id,
            plan_date=plan.plan_date,
            status=plan.status,
            posts=[],
        )

    def generate_posts(self, plan_id: int) -> List[PlannedPostRead]:
        plan = self.plan_repo.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        prompt = (
            f"Generate 5 LinkedIn/Instagram post drafts for "
            f"account {plan.account_id} on {plan.plan_date.date()}"
        )
        drafts = self.ai_client.generate_posts(prompt, n=5)

        created = []
        for text in drafts:
            pp = self.post_repo.create(
                PlannedPostCreate(content=text, scheduled_time=None)
            )
            # link it to the plan
            pp.plan_id = plan.id
            created.append(pp)

        return [
            PlannedPostRead(
                id=p.id,
                content=p.content,
                scheduled_time=p.scheduled_time,
                ai_suggested=bool(p.ai_suggested),
            )
            for p in created
        ]

    def update_post(
        self,
        plan_id: int,
        post_id: int,
        data: PlannedPostCreate,
    ) -> PlannedPostRead:
        post = self.post_repo.get(post_id)
        if not post or post.plan_id != plan_id:
            raise ValueError(f"Post {post_id} not found in plan {plan_id}")

        updated = self.post_repo.update(post, data)
        return PlannedPostRead(
            id=updated.id,
            content=updated.content,
            scheduled_time=updated.scheduled_time,
            ai_suggested=bool(updated.ai_suggested),
        )