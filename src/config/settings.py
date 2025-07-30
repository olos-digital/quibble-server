import os

from dotenv import load_dotenv

# Load environment variables from a .env file, allowing for easy configuration management.
load_dotenv()


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
AUTHOR_URN = os.getenv("AUTHOR_URN")


class Settings:
    """
    Application-wide settings class for FastAPI.
    
    This class encapsulates configuration values, loaded primarily from environment variables
    with sensible defaults.
    
    Attributes:
        DATABASE_URL (str): Connection string for the database (defaults to SQLite for local dev).
        SECRET_KEY (str): Key for JWT signing; should be unique and secret in production.
        ALGORITHM (str): JWT encoding algorithm (e.g., HS256); configurable for security needs.
    """
    
    # Defaults to a local SQLite file; override via .env var for production (e.g., PostgreSQL).
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Used for cryptographic operations like token signing; never commit to version control.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-secret")
    
    # Specifies the hashing method for tokens; HS256 is common but can be swapped for others.
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")


# Singleton instance: Provides global access to settings, useful for importing in services/routers.
settings = Settings()
