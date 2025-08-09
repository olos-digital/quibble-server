from fastapi import Request
from fastapi.responses import JSONResponse
from src.exceptions.common_exception import ValueNotFoundException


def register_value_not_found_exception_handler(app, logger):
    """
    Registers handler for ValueNotFoundException.

    Args:
        app (FastAPI): The FastAPI application instance.
        logger (logging.Logger): Logger instance to log missing value errors.
    """

    @app.exception_handler(ValueNotFoundException)
    async def value_not_found_exception_handler(request: Request, exc: ValueNotFoundException) -> JSONResponse:
        """
        Handler for ValueNotFoundException, typically raised when an expected value is missing.

        Logs the event and returns HTTP 404 with explanation.
        """
        logger.warning(f"ValueNotFound: {exc.message} at {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=404,
            content={"error": exc.message},
        )