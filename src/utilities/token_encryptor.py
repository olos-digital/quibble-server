import os
from cryptography.fernet import Fernet
from src.utilities import logger

key = os.getenv("TOKEN_ENCRYPTION_KEY")

fernet = Fernet(key)

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()
