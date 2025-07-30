import pytest
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.post_planning_router import PostPlanningRouter
from schemas.planning import (
    PostPlanCreate,
    PostPlanRead,
    PlannedPostCreate,
    PlannedPostRead,
)

class FakePostPlanningService:
    def create_plan(self, data: PostPlanCreate) -> PostPlanRead:
        # Echo back the minimal PostPlanRead shape
        return PostPlanRead(
            id=1,
            account_id=data.account_id,
            plan_date=data.plan_date,
            status="pending",
            posts=[],
        )

    def generate_posts(self, plan_id: int) -> list[PlannedPostRead]:
        now = datetime.now(timezone.utc)
        # Always returns two dummy PlannedPostRead objects
        return [
            PlannedPostRead(
                id=1,
                content="First post",
                scheduled_time=now,
                ai_suggested=True,
            ),
            PlannedPostRead(
                id=2,
                content="Second post",
                scheduled_time=None,
                ai_suggested=False,
            ),
        ]

    def update_post(self, plan_id: int, post_id: int, data: PlannedPostCreate) -> PlannedPostRead:
        # Echo back the updated post
        return PlannedPostRead(
            id=post_id,
            content=data.content,
            scheduled_time=data.scheduled_time,
            ai_suggested=False,
        )

@pytest.fixture
def client():
    app = FastAPI()
    fake_service = FakePostPlanningService()
    # Mount the router under "/planning"
    app.include_router(PostPlanningRouter(fake_service).router)
    return TestClient(app)

def test_create_plan(client):
    # Use an ISO datetime string for plan_date
    dt = "2025-07-30T12:00:00Z"
    payload = {"account_id": 42, "plan_date": dt}
    resp = client.post("/planning/", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == 1
    assert body["account_id"] == 42
    assert body["plan_date"] == dt
    assert body["status"] == "pending"
    assert body["posts"] == []

def test_generate_posts(client):
    # This route should always return two items
    resp = client.post("/planning/99/generate")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list) and len(data) == 2
    # Verify fields on the first generated post
    first = data[0]
    assert "ai_suggested" in first
    assert first["id"] == 1
    assert first["content"] == "First post"

def test_update_post(client):
    # Patch a single post — include scheduled_time if desired
    dt = "2025-07-31T08:30:00Z"
    payload = {"content": "updated!", "scheduled_time": dt}
    resp = client.patch("/planning/7/posts/3", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == 3
    assert body["content"] == "updated!"
    assert body["scheduled_time"] == dt
    assert body["ai_suggested"] is False