from typing import Annotated

from fastapi import Depends

from src.services.task_service import TaskService
from src.utils.unit_of_work import IUnitOfWork, UnitOfWork


async def get_task_service(uow: Annotated[IUnitOfWork, Depends(UnitOfWork)]) -> TaskService:
    return TaskService(uow)
