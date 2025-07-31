import logging
from typing import List, Set
from src.repositories.post_plan_repo import PostPlanRepo
from src.repositories.planned_post_repo import PlannedPostRepo
from src.schemas.planning import (
    PostPlanCreate,
    PostPlanRead,
    PlannedPostCreate,
    PlannedPostRead,
)
from src.utilities.mistral_client import MistralClient


logger = logging.getLogger(__name__)


class PlanNotFoundError(ValueError):
    pass


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
            logger.debug("Plan with id %s not found when generating posts", plan_id)
            raise PlanNotFoundError(f"Plan {plan_id} not found")

        prompt = (
            f"Generate 5 engaging, slightly varied LinkedIn/Instagram post drafts for "
            f"account {plan.account_id} on {plan.plan_date.date()}. "
            f"Make them suitable for professional audience, keep each under 300 characters, and avoid repetition."
        )

        try:
            drafts = self.ai_client.generate_posts(prompt, n=5)
        except Exception as e:
            logger.error("AI client failed to generate posts for plan %s: %s", plan_id, e)
            raise

        if not drafts or not isinstance(drafts, list):
            logger.warning("AI client returned no drafts or unexpected format for plan %s: %r", plan_id, drafts)
            raise ValueError("AI generation returned no valid drafts")

        seen: Set[str] = set()
        cleaned: List[str] = []
        for text in drafts:
            if not isinstance(text, str):
                continue
            normalized = text.strip()
            if not normalized:
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            cleaned.append(normalized)
            if len(cleaned) >= 5:  # cap to desired count
                break

        if not cleaned:
            logger.warning("All AI-generated drafts were empty/duplicate for plan %s", plan_id)
            raise ValueError("Generated drafts were invalid or empty")

        created = []
        for text in cleaned:
            try:
                pp = self.post_repo.create(
                    PlannedPostCreate(content=text, scheduled_time=None, plan_id=plan.id)
                )
                created.append(pp)
            except Exception as e:
                logger.error("Failed to persist planned post for plan %s: %s", plan_id, e)
                continue

        if not created:
            logger.error("Failed to create any planned posts for plan %s after AI generation", plan_id)
            raise RuntimeError("Failed to persist any generated posts")

        return [
            PlannedPostRead(
                id=p.id,
                content=p.content,
                scheduled_time=p.scheduled_time,
                ai_suggested=bool(getattr(p, "ai_suggested", True)),
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