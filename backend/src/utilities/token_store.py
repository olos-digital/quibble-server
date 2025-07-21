# TEMPORARY, in-memory cache ‑- disappear on server restart

from typing import Dict, Any

_token_cache: Dict[int, Any] = {}

def save_token(user_id: int, token_obj: Any) -> None:
    _token_cache[user_id] = token_obj

def get_token(user_id: int):
    return _token_cache.get(user_id)
