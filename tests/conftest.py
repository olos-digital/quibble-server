import pytest
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dependency_injector import providers

from src.database.models.base import Base
import src.database.models.user  # noqa: F401
import src.database.models.post  # noqa: F401

from src.database.db_config import get_db
from src.di.di_container import Container
from src.routers.auth_router import AuthRouter
from src.routers.linkedin_router import linkedin_router
from src.routers.user_router import UserRouter
from src.utilities.linkedin_helper import get_linkedin_token

# Shared in-memory SQLite (single connection so tables persist)
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
connection = engine.connect()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)


@pytest.fixture(scope="session", autouse=True)
def setup_schema():
    Base.metadata.create_all(bind=connection)
    yield
    Base.metadata.drop_all(bind=connection)
    connection.close()


@pytest.fixture()
def client():
    container = Container()
    # override config so AuthService gets deterministic values
    container.config.secret_key.from_value("test-secret")
    container.config.algorithm.from_value("HS256")
    container.config.hf_token.from_value("fake-hf")
    container.config.mistral_model_id.from_value("test-model")
    container.config.generated_posts_path.from_value("/tmp")
    # each request gets fresh test session
    container.db_session.override(providers.Factory(TestingSessionLocal))

    def fake_get_linkedin_token():
        return "linkedin-token-abc"

    # Dummy auth service: token format "fake-jwt-token-for-<username>"
    class DummyAuthService:
        def create_access_token(self, data: dict):
            return f"fake-jwt-token-for-{data.get('sub','')}"

        def get_current_user(self, request: Request):
            # manually parse Authorization header; mimic real dependency
            auth_header = request.headers.get("authorization", "")
            if not auth_header.lower().startswith("bearer "):
                raise HTTPException(status_code=401, detail="Not authenticated")
            token = auth_header[7:]
            if not token.startswith("fake-jwt-token-for-"):
                raise HTTPException(status_code=401, detail="Invalid token")
            username = token.replace("fake-jwt-token-for-", "")
            return username  # routers expect username string

    app = FastAPI()

    # Auth router using dummy auth service
    auth_router: AuthRouter = container.auth_router()
    auth_router.auth_service = DummyAuthService()
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])

    # User router also needs dummy auth service
    user_router = UserRouter(auth_service=DummyAuthService())
    app.include_router(user_router.router, prefix="/users", tags=["users"])

    app.include_router(linkedin_router)

    # override get_db to ensure isolated short-lived session per request
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_linkedin_token] = lambda: "linkedin-token-abc"

    return TestClient(app)