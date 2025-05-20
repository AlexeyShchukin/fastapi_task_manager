from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from uvicorn import run
from fastapi import FastAPI

from src.api.endpoints.ws import ws_router
from src.api.endpoints.auth import auth_router
from src.api.endpoints.tasks import task_router
from src.api.endpoints.users import user_router
from src.api.middleware.middleware import LoggingMiddleware, configure_cors
from src.core.lifespan import lifespan
from src.exceptions.handlers import validation_exception_handler, handle_db_error, handle_unexpected_error

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(ws_router)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, handle_db_error)
app.add_exception_handler(Exception, handle_unexpected_error)
app.add_middleware(LoggingMiddleware)
configure_cors(app)


if __name__ == "__main__":
    run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )
