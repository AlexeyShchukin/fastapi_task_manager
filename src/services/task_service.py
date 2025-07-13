from uuid import UUID

from fastapi import HTTPException, status

from src.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate
from src.api.schemas.user import UserPublic, UserInternal
from src.services.permission_service import verify_ownership
from src.utils.unit_of_work import IUnitOfWork


class TaskService:
    """Service layer for managing tasks."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_task(self, task: TaskCreate, user: UserPublic) -> TaskFromDB:
        """
        Adds a new task for a given user.
        Args:
            task: The task data for creation.
            user: The user creating the task.
        Returns: The created TaskFromDB object.
       """
        task_dict: dict = task.model_dump()
        task_dict["owner_uuid"] = user.uuid
        async with self.uow as uow:
            task_from_db = await uow.tasks.add_one(task_dict)
            task_to_return = TaskFromDB.model_validate(task_from_db)
            await uow.commit()
            return task_to_return

    async def get_tasks(
            self,
            skip: int = 0,
            limit: int = 10,
            owner_id: UUID | None = None
    ) -> list[TaskFromDB]:
        """
        Retrieves a list of tasks.
        Args:
            skip: Number of tasks to skip.
            limit: Maximum number of tasks to return.
            owner_id: Optional UUID of the task owner to filter by.
        Returns:
            A list of TaskFromDB objects.
        """
        async with self.uow as uow:
            tasks: list = await uow.tasks.find_all(owner_id=owner_id, skip=skip, limit=limit)
            return [TaskFromDB.model_validate(task) for task in tasks]

    async def get_task_by_id(self, task_id: UUID) -> TaskFromDB | None:
        """
        Retrieves a single task by its ID.
        Args:
            task_id: The UUID of the task.
        Returns:
            The TaskFromDB object if found.
        Raises:
            HTTPException: If the task is not found.
        """
        async with self.uow as uow:
            task = await uow.tasks.find_by_id(task_id)
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            return TaskFromDB.model_validate(task) if task else None

    async def update_task(
            self,
            task_id: UUID,
            task_update: TaskUpdate,
            current_user: UserInternal
    ) -> TaskFromDB | None:
        """
        Updates an existing task.
        Args:
            task_id: The UUID of the task to update.
            task_update: The updated task data.
            current_user: The user attempting to update the task.
        Returns:
            The updated TaskFromDB object.
        Raises:
            HTTPException: If the task is not found or permission is denied.
        """
        async with self.uow as uow:
            task = await uow.tasks.find_by_id(task_id)
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            verify_ownership(current_user, task.owner_uuid)

            if task_update.title is not None:
                task.title = task_update.title
            if task_update.description is not None:
                task.description = task_update.description
            if task_update.completed is not None:
                task.completed = task_update.completed

            task_to_return = TaskFromDB.model_validate(task)
            await uow.commit()
            return task_to_return

    async def delete_task(self, task_id: UUID, current_user: UserInternal) -> None:
        """
       Deletes a task.
       Args:
           task_id: The UUID of the task to delete.
           current_user: The user attempting to delete the task.
       Raises:
           HTTPException: If the task is not found or permission is denied.
       """
        async with self.uow as uow:
            task = await uow.tasks.find_by_id(task_id)
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            verify_ownership(current_user, task.owner_uuid)

            await uow.tasks.delete(task)
            await uow.commit()
