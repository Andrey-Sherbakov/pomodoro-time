from fastapi import Request, Response
from fastapi.responses import JSONResponse

from src.core.log_config import logger


async def exception_middleware(request: Request, call_next):
    try:
        response: Response = await call_next(request)
    except Exception as e:
        logger.error("Request to %s failed: %r", request.url.path, e)
        response = JSONResponse(content={"detail": "Something went wrong"}, status_code=500)
    return response
