from fastapi.exceptions import RequestValidationError
from uvicorn import run
from fastapi import FastAPI

from src.api.endpoints.auth import auth_router
from src.api.endpoints.tasks import task_router
from src.api.endpoints.users import user_router
from src.api.middleware.middleware import LoggingMiddleware, configure_cors
from src.exceptions.handlers import validation_exception_handler

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_middleware(LoggingMiddleware)
configure_cors(app)

if __name__ == "__main__":
    run(app="main:app")
