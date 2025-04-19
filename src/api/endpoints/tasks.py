from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from src.api.dependencies.task_dependency import get_task_service
from src.api.dependencies.user_dependency import get_user_from_token
from src.api.schemas.task import TaskFromDB, TaskCreate, TaskUpdate
from src.api.schemas.user import UserFromDB
from src.services.task_service import TaskService

task_router = APIRouter(
    prefix="/api/v1",
    tags=["Tasks"]
)


@task_router.post("/", response_model=TaskFromDB)
async def create_task(task_data: TaskCreate,
                      task_service: Annotated[TaskService, Depends(get_task_service)],
                      user: Annotated[UserFromDB, Depends(get_user_from_token)]
                      ) -> TaskFromDB:
    return await task_service.add_task(task_data, user)


@task_router.get("/", response_model=list[TaskFromDB])
async def get_tasks(
        task_service: Annotated[TaskService, Depends(get_task_service)],
        skip: int = 0,
        limit: int = 10
) -> list[TaskFromDB]:
    if limit > 100:
        limit = 100
    return await task_service.get_tasks(skip=skip, limit=limit)


@task_router.get("/tasks/{task_id}", response_model=TaskFromDB)
async def get_task_by_id(
        task_id: UUID,
        task_service: Annotated[TaskService, Depends(get_task_service)]
) -> TaskFromDB:
    task = await task_service.get_task_by_id(task_id)
    return task


@task_router.patch("/tasks/{task_id}", response_model=TaskFromDB)
async def update_task(
        task_id: UUID,
        task_update: TaskUpdate,
        task_service: Annotated[TaskService, Depends(get_task_service)]
) -> TaskFromDB:
    updated_task = await task_service.update_task(task_id, task_update)
    return updated_task


@task_router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "Task deleted successfully"}}
)
async def delete_task(
        task_id: UUID,
        task_service: Annotated[TaskService, Depends(get_task_service)]
) -> Response:
    await task_service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)