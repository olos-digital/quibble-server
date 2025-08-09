from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def setup_exception_handlers(app, logger):
    """
    Registers global exception handlers on the FastAPI app to provide consistent error
    responses and centralized logging for various exception types.

    Args:
        app (FastAPI): The FastAPI application instance.
        logger (logging.Logger): Configured logger instance to record error details.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handler for FastAPI's HTTPException, typically raised intentionally to
        signal HTTP errors like 404, 403, 401, etc.

        Logs exception details with traceback and returns JSON error response.
        """
        logger.error(f"HTTPException: {exc.detail} (path: {request.url.path})", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handler for request validation errors triggered by Pydantic model validation failures.

        Logs detailed validation errors and returns HTTP 422 with error info.
        """
        logger.error(
            f"Validation error at {request.url.path}: {exc.errors()}",
            exc_info=True
        )
        return JSONResponse(
            status_code=422,
            content={"error": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Catch-all handler for uncaught exceptions not handled by specific handlers.

        Logs full stack trace and returns HTTP 500 with generic error message to avoid
        exposing internal details.
        """
        logger.error(
            f"Unhandled exception at {request.url.path}: {str(exc)}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
