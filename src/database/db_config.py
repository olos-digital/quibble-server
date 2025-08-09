import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utilities import logger

logger = logger.setup_logger("DBConfig logger")


# Database engine: Core connection pool for SQLAlchemy; configured with the app's DATABASE_URL.
# The connect_args handle SQLite-specific threading behavior to prevent concurrency issues
# in FastAPI's async environment.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
logger.info(f"Using database URL: {DATABASE_URL}")

engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory: Creates ORM sessions for database interactions; configured without
# autoflush/autocommit to give explicit control over transactions in API endpoints.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
	"""
	Dependency function for FastAPI to provide a database session.

	This generator yields a new SQLAlchemy session per request, ensuring isolation
	and proper resource management. It is injected into routes via Depends(get_db)
	to handle database operations transactionally

	Yields:
		Session: An active database session.

	Finally:
		Closes the session to release resources after the request completes.
	"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
