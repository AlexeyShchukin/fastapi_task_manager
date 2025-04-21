from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from fastapi import Request, status
from sqlalchemy.exc import DatabaseError

from src.loggers.loggers import logger


def validation_exception_handler(
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


def handle_db_error(request: Request, exc: DatabaseError) -> ORJSONResponse:
    logger.error("Unhandled database error", exc_info=exc)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error has occurred."
                            "Our admins are already working on it."}
    )

