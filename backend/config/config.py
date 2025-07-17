import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
AUTHOR_URN = os.getenv("AUTHOR_URN")

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

settings = Settings()