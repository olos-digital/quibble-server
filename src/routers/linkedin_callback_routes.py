from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from src.oauth.linkedin_oauth import exchange_authorization_code
from src.services.auth_service import AuthService
from src.utilities.token_store import save_token


class LinkedinCallbackRoute:
	def __init__(self, auth_service: AuthService):
		self.auth_service = auth_service
		self.router = APIRouter()
		self._attach_routes()

	def _attach_routes(self):
		@self.router.get("/linkedin/callback")
		def linkedin_callback(
				code: str,
				state: str,
				current_user=Depends(self.auth_service.get_current_user),  # returns User
		):
			token = exchange_authorization_code(code)
			save_token(current_user.id, token)
			return RedirectResponse("/dashboard?linkedin=ok")
