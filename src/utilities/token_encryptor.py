import os
from cryptography.fernet import Fernet

key = os.environ["TOKEN_ENCRYPTION_KEY"].encode()

fernet = Fernet(key)

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()
