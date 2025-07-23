from typing import Optional

from passlib.context import CryptContext


# bcrypt hashing with auto-deprecation handling;
# ensures secure, adaptive password storage compliant with best practices.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password for secure storage.
    
    This utility function uses the configured CryptContext to generate a bcrypt hash,
    suitable for storing in databases during user registration or updates in FastAPI
    apps.
    
    Args:
        password (str): Plain-text password to hash.
    
    Returns:
        str: Hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored hash.
    
    This function checks if the provided password matches the hash, used in
    authentication flows (e.g., login endpoints) to validate user credentials
    securely without exposing hashes.
    
    Args:
        plain_password (str): Input password to verify.
        hashed_password (str): Stored hashed password for comparison.
    
    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
