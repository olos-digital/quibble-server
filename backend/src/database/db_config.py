from config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database engine: Core connection pool for SQLAlchemy; configured with the app's DATABASE_URL.
# The connect_args handle SQLite-specific threading behavior to prevent concurrency issues
# in FastAPI's async environment.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)


# Session factory: Creates ORM sessions for database interactions; configured without
# autoflush/autocommit to give explicit control over transactions in API endpoints.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Declarative base: Foundation for all SQLAlchemy models; used to define tables and
# relationships, enabling schema creation/migration via Alembic in FastAPI projects.
Base = declarative_base()

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
