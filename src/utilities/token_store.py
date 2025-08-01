from typing import Dict, Any

# temporary storage for tokens keyed by user ID; disappears on server restart
_token_cache: Dict[int, Any] = {}


def save_token(user_id: int, token_obj: Any) -> None:
	"""
	Saves a token object to the in-memory cache.

	This function stores arbitrary token data associated with a user ID, used in
	FastAPI dependencies for quick, session-like access without database hits.

	Args:
		user_id (int): Unique identifier of the user.
		token_obj (Any): Token data to cache (e.g., LinkedInToken instance).
	"""
	_token_cache[user_id] = token_obj


def get_token(user_id: int):
	"""
	Retrieves a token object from the in-memory cache.

	This function fetches cached token data by user ID, returning None if not found.
	It supports FastAPI's dependency injection for token-based operations, with the
	understanding that cache misses require re-authentication (e.g., via OAuth flows).

	Args:
		user_id (int): Unique identifier of the user.

	Returns:
		Any | None: Cached token object or None if not present.
	"""
	return _token_cache.get(user_id)
