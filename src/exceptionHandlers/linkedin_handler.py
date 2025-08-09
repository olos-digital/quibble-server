from fastapi import Request
from fastapi.responses import JSONResponse
from src.exceptions.linkedin_exception import LinkedInConnectionException


def register_linkedin_exception_handler(app, logger):
    """
    Registers handler for LinkedIn connection errors.

    Args:
        app (FastAPI): The FastAPI application instance.
        logger (logging.Logger): Logger instance to capture exception details.
    """

    @app.exception_handler(LinkedInConnectionException)
    async def linkedin_exception_handler(request: Request, exc: LinkedInConnectionException) -> JSONResponse:
        """
        Handler for LinkedInConnectionException, raised when LinkedIn API fails or is unreachable.

        Logs the error and returns HTTP 502 with message.
        """
        logger.error(f"LinkedIn error: {exc.message} at {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=502,
            content={"error": exc.message},
        )