import pytest
from dependency_injector import providers
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.di.di_container import Container
from src.database.models.base import Base
# force import of models so they’re registered with Base
import src.database.models.user  # noqa: F401
import src.database.models.post  # noqa: F401

from src.database.db_config import get_db
from src.routers.auth_router import AuthRouter
from src.routers.user_router import UserRouter
from src.services.user_service import UserService

# --- in-memory test DB (single shared connection) ---
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
# Use connect_args to allow same thread usage
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# create a single connection and keep it open
connection = engine.connect()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)


@pytest.fixture(scope="session", autouse=True)
def setup_schema():
    # create all tables once on the shared connection
    Base.metadata.create_all(bind=connection)
    yield
    Base.metadata.drop_all(bind=connection)
    connection.close()


@pytest.fixture()
def test_app(monkeypatch):
    container = Container()
    container.config.secret_key.from_value("test-secret")
    container.config.algorithm.from_value("HS256")
    container.config.hf_token.from_value("fake-hf")
    container.config.mistral_model_id.from_value("test-model")
    container.config.generated_posts_path.from_value("/tmp")
    container.db_session.override(providers.Factory(TestingSessionLocal))

    # Dummy auth service for deterministic token + current_user resolution
    class DummyAuthService:
        def create_access_token(self, data: dict):
            return f"fake-jwt-token-for-{data.get('sub', '')}"

        def get_current_user(self, request: Request) -> str:
            auth_header = request.headers.get("authorization", "")
            if not auth_header.lower().startswith("bearer "):
                raise HTTPException(status_code=401)
            token = auth_header[7:]
            username = token.replace("fake-jwt-token-for-", "")
            return username

    auth_router: AuthRouter = container.auth_router()
    auth_router.auth_service = DummyAuthService()
    user_service = UserService(container.db_session())
    user_router = UserRouter(auth_service=DummyAuthService(), user_service=user_service)

    app = FastAPI()
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    app.include_router(user_router.router, prefix="/users", tags=["users"])

    # override get_db to use the shared session
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    return app


@pytest.fixture()
def client(test_app):
    return TestClient(test_app)