from fastapi import Request
from fastapi.responses import JSONResponse
from exceptions.auth import AuthException


def register_auth_exception_handler(app, logger):
    """
    Registers handler for authentication-related exceptions.

    Args:
        app (FastAPI): The FastAPI application instance.
        logger (logging.Logger): Logger to capture exception details.
    """

    @app.exception_handler(AuthException)
    async def auth_exception_handler(request: Request, exc: AuthException) -> JSONResponse:
        """
        Handler for AuthException, typically raised when authentication fails.

        Logs the error and returns HTTP 401 with relevant message.
        """
        logger.warning(f"AuthException: {exc.message} at {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=401,
            content={"error": exc.message},
        )