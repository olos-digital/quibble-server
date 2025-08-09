from fastapi import HTTPException
from starlette import status

class XApiException(HTTPException):
    def __init__(self, detail: str = "Error interacting with X (Twitter) API"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)