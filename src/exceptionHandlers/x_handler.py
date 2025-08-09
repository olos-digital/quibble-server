from fastapi import Request
from fastapi.responses import JSONResponse
from src.exceptions.x_exception import XApiException
from src.utilities import logger

logger = logger.setup_logger("XApiExceptionHandler")

async def x_api_exception_handler(request: Request, exc: XApiException):
    logger.error(f"XApiException caught: {exc.detail}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )