from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from fastapi import Request, status
from sqlalchemy.exc import SQLAlchemyError

from src.loggers.loggers import logger


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
) -> ORJSONResponse:
    err = exc.errors()[0]
    field = err["loc"][-1]
    message = err["msg"]
    body = exc.body

    logger.error(
        """Request: %s %s 
        Validation error: [field: %s]
        [message: %s]
        [body: %s]""",
        request.method,
        request.url,
        field,
        message,
        body
    )

    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "error": "Validation error",
            "details": [
                {
                    "field": err["loc"][-1],
                    "message": err["msg"]
                }
                for err in exc.errors()
            ],
            "body": exc.body
        })
    )


async def handle_db_error(request: Request, exc: SQLAlchemyError) -> ORJSONResponse:
    logger.error(
        "Database error during request: %s %s",
        request.method,
        request.url,
        exc_info=exc
    )
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error has occurred. Our admins are already working on it."}
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> ORJSONResponse:
    logger.error(
        "Unexpected error occurred",
        request.method,
        request.url,
        exc_info=exc
    )
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error. Please try again later."}
    )
