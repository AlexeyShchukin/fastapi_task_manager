from fastapi import HTTPException

from src.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate
from src.api.schemas.user import UserFromDB
from src.utils.unit_of_work import IUnitOfWork


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_task(self, task: TaskCreate, user: UserFromDB) -> TaskFromDB:
        task_dict: dict = task.model_dump()
        task_dict["owner_id"] = user.id
        async with self.uow as uow:
            task_from_db = await uow.task.add_one(task_dict)
            task_to_return = TaskFromDB.model_validate(task_from_db)
            await uow.commit()
            return task_to_return

    async def get_tasks(self, skip: int = 0, limit: int = 10) -> list[TaskFromDB]:
        async with self.uow as uow:
            tasks: list = await uow.task.find_all(skip=skip, limit=limit)
            return [TaskFromDB.model_validate(task) for task in tasks]

    async def get_task_by_id(self, task_id: int) -> TaskFromDB | None:
        async with self.uow as uow:
            task = await uow.task.find_by_id(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            return TaskFromDB.model_validate(task) if task else None

    async def update_task(self, task_id: int, task_update: TaskUpdate) -> TaskFromDB | None:
        async with self.uow as uow:
            task = await uow.task.find_by_id(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            if task_update.title is not None:
                task.title = task_update.title
            if task_update.description is not None:
                task.description = task_update.description
            if task_update.completed is not None:
                task.completed = task_update.completed
            task_to_return = TaskFromDB.model_validate(task)
            await uow.commit()
            return task_to_return

    async def delete_task(self, task_id: int) -> None:
        async with self.uow as uow:
            task = await uow.task.find_by_id(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            await uow.task.delete(task)
            await uow.commit()
