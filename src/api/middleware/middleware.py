from time import perf_counter

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.loggers.loggers import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = perf_counter()
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        process_time = perf_counter() - start_time
        logger.info(f"Response: {response.status_code} (handling {process_time:.4f} seconds)")

        return response


def configure_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
