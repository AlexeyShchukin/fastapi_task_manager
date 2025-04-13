from src.api.schemas.task import TaskCreate, TaskFromDB
from src.utils.unit_of_work import IUnitOfWork


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_task(self, task: TaskCreate) -> TaskFromDB:
        task_dict: dict = task.model_dump()
        async with self.uow as uow:
            task_from_db = await uow.task.add_one(task_dict)
            task_to_return = TaskFromDB.model_validate(task_from_db)
            await uow.commit()
            return task_to_return

    async def get_tasks(self) -> list[TaskFromDB]:
        async with self.uow as uow:
            tasks: list = await uow.task.find_all()
            return [TaskFromDB.model_validate(task) for task in tasks]