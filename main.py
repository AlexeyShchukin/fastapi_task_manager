from uvicorn import run
from fastapi import FastAPI

from src.api.endpoints.tasks import task_router
from src.api.endpoints.users import user_router


app = FastAPI()

app.include_router(task_router)
app.include_router(user_router)

if __name__ == "__main__":
    run(app="main:app")
