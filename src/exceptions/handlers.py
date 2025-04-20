from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request, status

from src.loggers.loggers import logger


def validation_exception_handler(request: Request, exc: RequestValidationError):
    err = exc.errors()[0]
    field = err["loc"][-1]
    message = err["msg"]
    body = exc.body

    log_message = (f"""Request URL: {request.url}, Method: {request.method}, Validation error: 
    field: {field}, message: {message}, 
    body: {body}""")

    logger.error(log_message)

    return JSONResponse(
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

