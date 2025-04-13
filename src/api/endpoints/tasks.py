from fastapi import APIRouter, Depends

from src.api.schemas.task import TaskFromDB, TaskCreate
from src.services.task_service import TaskService
from src.utils.unit_of_work import IUnitOfWork, UnitOfWork

task_router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


async def get_task_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> TaskService:
    return TaskService(uow)


@task_router.post("/", response_model=TaskFromDB)
async def create_task(task_data: TaskCreate, task_service: TaskService = Depends(get_task_service)):
    return await task_service.add_task(task_data)


@task_router.get("/", response_model=list[TaskFromDB])
async def get_tasks(task_service: TaskService = Depends(get_task_service)):
    return await task_service.get_tasks()
