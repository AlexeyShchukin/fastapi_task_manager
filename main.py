from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DatabaseError
from uvicorn import run
from fastapi import FastAPI

from src.api.endpoints import ws
from src.api.endpoints.auth import auth_router
from src.api.endpoints.tasks import task_router
from src.api.endpoints.users import user_router
from src.api.middleware.middleware import LoggingMiddleware, configure_cors
from src.exceptions.handlers import validation_exception_handler, handle_db_error

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DatabaseError, handle_db_error)
app.add_middleware(LoggingMiddleware)
configure_cors(app)
app.include_router(ws.router)

if __name__ == "__main__":
    run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )
