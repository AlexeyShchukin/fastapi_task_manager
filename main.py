import uvicorn
from fastapi import FastAPI

from src.api.endpoints.tasks import task_router

app = FastAPI()

app.include_router(task_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app")
