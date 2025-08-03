from typing import List

from src.generation.text.mistral_client import MistralClient
from src.repositories.planned_post_repo import PlannedPostRepo
from src.repositories.post_plan_repo import PostPlanRepo
from src.schemas.planning import (
	PostPlanCreate,
	PostPlanRead,
	PlannedPostCreate,
	PlannedPostRead,
)
from src.utilities import logger

logger = logger.setup_logger("PostPlanningService")


class PostPlanningService:
	"""
	Service class responsible for business logic related to post planning.
	The class handles creation of post plans, generation of planned posts using AI,
	and update of individual planned posts.
	"""

	def __init__(
			self,
			plan_repo: PostPlanRepo,
			post_repo: PlannedPostRepo,
			ai_client: MistralClient,
	):
		self.plan_repo = plan_repo
		self.post_repo = post_repo
		self.ai_client = ai_client
		logger.info("PostPlanningService initialized with repositories and AI client.")

	def create_plan(self, data: PostPlanCreate) -> PostPlanRead:
		"""
		Create a new post plan record and return a read model.
		Args:
			data (PostPlanCreate): Data required to create a new post plan.
		Returns:
			PostPlanRead: Representation of the created post plan without posts yet.
		Raises:
			Exception: If there is an error during creation, it will be logged and raised.
		"""
		logger.info(f"Creating post plan for account_id={data.account_id} on date={data.plan_date}")

		try:
			plan = self.plan_repo.create(data)
			logger.info(f"Post plan created successfully with id={plan.id}")

			return PostPlanRead(
				id=plan.id,
				account_id=plan.account_id,
				plan_date=plan.plan_date,
				status=plan.status,
				posts=[],
			)
		except Exception as e:
			logger.error(f"Failed to create post plan for account_id={data.account_id}: {e}", exc_info=True)
			raise

	def get_plan(self, plan_id: int) -> PostPlanRead:
		"""
		Retrieve a post plan along with all its associated planned posts.

		This will fetch the plan by ID, validate its existence, then load all
		planned posts linked to it (via the repository's filtering). The result
		is normalized into the read model including the list of posts.

		Args:
		    plan_id (int): Identifier of the post plan to fetch.

		Returns:
		    PostPlanRead: Representation of the plan including its current posts.

		Raises:
		    ValueError: If the specified post plan does not exist.
		"""
		plan = self.plan_repo.get(plan_id)
		if not plan:
			raise ValueError(f"Plan {plan_id} not found")

		posts = self.post_repo.list_by_plan(plan.id)

		planned_reads = [
			PlannedPostRead(
				id=p.id,
				content=p.content,
				scheduled_time=p.scheduled_time,
				ai_suggested=bool(p.ai_suggested),
			)
			for p in posts
		]

		return PostPlanRead(
			id=plan.id,
			account_id=plan.account_id,
			plan_date=plan.plan_date,
			status=plan.status,
			posts=planned_reads,
		)

	def generate_posts(self, plan_id: int, count: int = 1) -> List[PlannedPostRead]:
		"""
		Generate AI-suggested post drafts for a given post plan.
		Steps:
			- Validate that the plan exists.
			- Build a prompt using the account and date from the plan.
			- Call AI client to generate 5 post drafts.
			- Persist each draft as a planned post linked to the plan.
			- Return a list of read models representing the created planned posts.
		Args:
			plan_id (int): Identifier of the post plan to generate posts for.
		Returns:
			List[PlannedPostRead]: List of planned posts created.
		Raises:
			ValueError: If the specified post plan does not exist.
		"""
		logger.info(f"Generating posts for plan_id={plan_id}")

		plan = self.plan_repo.get(plan_id)
		if not plan:
			logger.warning(f"Post plan with id={plan_id} not found")
			raise ValueError(f"Plan {plan_id} not found")

		prompt = (
			f"Generate LinkedIn/Instagram post draft for "
			f"account {plan.account_id} on {plan.plan_date.date()}"
		)
		logger.debug(f"AI prompt constructed: {prompt}")

		try:
			raw_drafts = self.ai_client.generate_posts(prompt, n=count)
			logger.info(f"Received {len(raw_drafts)} drafts from AI client for plan_id={plan_id}")
		except Exception as e:
			logger.error(f"AI client failed to generate posts for plan_id={plan_id}: {e}", exc_info=True)
			raise

		drafts: List[str] = [self._unwrap_draft_item(item) for item in raw_drafts]

		created = []
		for text in drafts:
			try:
				pp = self.post_repo.create_with_plan(
					plan.id,
					text,
					scheduled_time=None,
					ai_suggested=1,
				)
				# Associate the planned post with the post plan
				pp.plan_id = plan.id
				created.append(pp)
				logger.debug(f"Created planned post with id={pp.id} linked to plan_id={plan_id}")

			except Exception as e:
				logger.error(f"Failed to persist planned post draft for plan_id={plan_id}: {e}", exc_info=True)

		result = [
			PlannedPostRead(
				id=p.id,
				content=p.content,
				scheduled_time=p.scheduled_time,
				ai_suggested=bool(p.ai_suggested),
			)
			for p in created
		]

		logger.info(f"Generated and persisted {len(result)} planned posts for plan_id={plan_id}")
		return result

	def update_post(
			self,
			plan_id: int,
			post_id: int,
			data: PlannedPostCreate,
	) -> PlannedPostRead:
		"""
		 Update content or scheduled time of an existing planned post within a plan.
		 Args:
		     plan_id (int): Identifier of the post plan containing the post.
		     post_id (int): Identifier of the planned post to update.
		     data (PlannedPostCreate): Data containing updates for the planned post.
		 Returns:
		     PlannedPostRead: Updated planned post data.
		 Raises:
		     ValueError: If the planned post doesn't exist or doesn't belong to the given plan.
		 Logs:
		     Info on beginning and successful update.
		     Warning if post not found or mismatched plan.
		     Error with stack trace for unexpected failures.
		 """
		logger.info(f"Updating planned post id={post_id} in plan_id={plan_id}")
		post = self.post_repo.get(post_id)
		if not post:
			logger.warning(f"Planned post id={post_id} not found")
			raise ValueError(f"Post {post_id} not found in plan {plan_id}")

		if post.plan_id != plan_id:
			logger.warning(f"Planned post id={post_id} does not belong to plan_id={plan_id}")
			raise ValueError(f"Post {post_id} not found in plan {plan_id}")

		try:
			updated = self.post_repo.update(post, data)
			logger.info(f"Planned post id={post_id} updated successfully")
		except Exception as e:
			logger.error(f"Failed to update planned post id={post_id}: {e}", exc_info=True)
			raise

		return PlannedPostRead(
			id=updated.id,
			content=updated.content,
			scheduled_time=updated.scheduled_time,
			ai_suggested=bool(updated.ai_suggested),
		)

	@staticmethod
	def _unwrap_draft_item(item) -> str:
		# Extract the actual text from various possible shapes
		if isinstance(item, str):
			return item
		if isinstance(item, dict):
			# New Mistral-style: choices -> message -> content
			if choices := item.get("choices"):
				if isinstance(choices, list) and choices:
					first = choices[0]
					if isinstance(first, dict):
						message = first.get("message")
						if isinstance(message, dict):
							content = message.get("content")
							if isinstance(content, str):
								return content
			# fallback to common keys
			if text := item.get("content") or item.get("text"):
				if isinstance(text, str):
					return text
			# last resort: stringify but make it compact
			return str(item)
		return str(item)
