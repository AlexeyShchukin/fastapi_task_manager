import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException, status

from src.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate
from src.api.schemas.user import UserPublic, UserInternal
from src.services.task_service import TaskService
from src.utils.unit_of_work import IUnitOfWork


@pytest.mark.unit
@pytest.mark.task_service
class TestTaskService:
    """
    Unit tests for the TaskService.
    """

    async def test_add_task_success(
            self,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            sample_task_create: TaskCreate,
            sample_user_public: UserPublic,
            mock_task_model: AsyncMock
    ):
        """Test case for successful task addition."""

        mock_uow.tasks.add_one.return_value = mock_task_model

        result = await task_service.add_task(sample_task_create, sample_user_public)

        mock_uow.tasks.add_one.assert_called_once_with({
            "title": sample_task_create.title,
            "description": sample_task_create.description,
            "owner_uuid": sample_user_public.uuid
        })
        mock_uow.commit.assert_called_once()
        assert isinstance(result, TaskFromDB)
        assert result.title == sample_task_create.title
        assert result.owner_uuid == sample_user_public.uuid
        assert result.uuid == mock_task_model.uuid

    async def test_get_tasks_success_default_params(
            self,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            mock_task_model: AsyncMock,
    ):
        """
        Test case for successful retrieval of tasks with default skip/limit and no owner_id.
        """
        mock_uow.tasks.find_all.return_value = [mock_task_model]

        result = await task_service.get_tasks()

        mock_uow.tasks.find_all.assert_called_once_with(owner_id=None, skip=0, limit=10)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TaskFromDB)

        assert result[0].uuid == mock_task_model.uuid
        assert result[0].title == mock_task_model.title
        assert result[0].owner_uuid == mock_task_model.owner_uuid
        assert result[0].description == mock_task_model.description

    async def test_get_tasks_success_with_filters(
            self,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            sample_user_public: UserPublic,
            mock_task_model: AsyncMock,
    ):
        """
        Test case for successful retrieval of tasks with owner_id, skip, and limit filters.
        """

        mock_task_model_2 = AsyncMock()
        mock_task_model_2.uuid = uuid4()
        mock_task_model_2.title = "Another Task"
        mock_task_model_2.description = "Another description."
        mock_task_model_2.completed = True
        mock_task_model_2.created_at = datetime.now(timezone.utc)
        mock_task_model_2.owner_uuid = sample_user_public.uuid

        mock_uow.tasks.find_all.return_value = [mock_task_model, mock_task_model_2]

        test_skip = 1
        test_limit = 1
        test_owner_id = sample_user_public.uuid

        result = await task_service.get_tasks(
            skip=test_skip,
            limit=test_limit,
            owner_id=test_owner_id
        )

        mock_uow.tasks.find_all.assert_called_once_with(
            owner_id=test_owner_id,
            skip=test_skip,
            limit=test_limit
        )

        assert isinstance(result, list)
        assert len(result) == 2

        assert result[0].uuid == mock_task_model.uuid
        assert result[0].title == mock_task_model.title
        assert result[0].owner_uuid == mock_task_model.owner_uuid

        assert result[1].uuid == mock_task_model_2.uuid
        assert result[1].title == mock_task_model_2.title
        assert result[1].owner_uuid == mock_task_model_2.owner_uuid

    async def test_get_task_by_id_success(
            self,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            mock_task_model: AsyncMock,
    ):
        """Test case for successful retrieval of a single task by its id"""

        mock_uow.tasks.find_by_id.return_value = mock_task_model

        result = await task_service.get_task_by_id(mock_task_model.uuid)

        mock_uow.tasks.find_by_id.assert_called_once_with(mock_task_model.uuid)

        assert isinstance(result, TaskFromDB)
        assert result.uuid == mock_task_model.uuid
        assert result.title == mock_task_model.title
        assert result.owner_uuid == mock_task_model.owner_uuid

    async def test_get_task_by_id_not_found(
            self,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
    ):
        """
        Test case for task not found when retrieving by id.
        """
        mock_uow.tasks.find_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await task_service.get_task_by_id(uuid4())

        mock_uow.tasks.find_by_id.assert_called_once()

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Task not found"

    @patch('src.services.task_service.verify_ownership')
    async def test_update_task_success(
            self,
            mock_verify_ownership: AsyncMock,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            mock_task_model: AsyncMock,
            simple_user_internal: UserInternal,
    ):
        """Test case for successful task update."""

        mock_uow.tasks.find_by_id.return_value = mock_task_model
        task_update_data = TaskUpdate(
            title="Updated Title",
            description="Updated description.",
            completed=True
        )
        result = await task_service.update_task(
            task_id=mock_task_model.uuid,
            task_update=task_update_data,
            current_user=simple_user_internal
        )
        mock_uow.tasks.find_by_id.assert_called_once_with(mock_task_model.uuid)
        mock_verify_ownership.assert_called_once_with(simple_user_internal, mock_task_model.owner_uuid)
        mock_uow.commit.assert_called_once()
        assert mock_task_model.title == task_update_data.title
        assert mock_task_model.description == task_update_data.description
        assert mock_task_model.completed == task_update_data.completed
        assert isinstance(result, TaskFromDB)
        assert result.uuid == mock_task_model.uuid
        assert result.title == task_update_data.title
        assert result.description == task_update_data.description
        assert result.completed == task_update_data.completed
        assert result.owner_uuid == mock_task_model.owner_uuid

    @patch('src.services.task_service.verify_ownership')
    async def test_update_task_not_found(
            self,
            mock_verify_ownership: AsyncMock,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            simple_user_internal: UserInternal,
    ):
        """Test case for task not found during update."""

        mock_uow.tasks.find_by_id.return_value = None
        task_update_data = TaskUpdate(title="New Title")
        some_uuid = uuid4()
        with pytest.raises(HTTPException) as exc_info:
            await task_service.update_task(
                task_id=some_uuid,
                task_update=task_update_data,
                current_user=simple_user_internal
            )
        mock_uow.tasks.find_by_id.assert_called_once_with(some_uuid)
        mock_verify_ownership.assert_not_called()
        mock_uow.commit.assert_not_called()
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Task not found"

    @patch('src.services.task_service.verify_ownership')
    async def test_update_task_permission_denied(
            self,
            mock_verify_ownership: AsyncMock,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            mock_task_model: AsyncMock,
            simple_user_internal: UserInternal,
    ):
        """Test case for permission denied when updating a task."""

        mock_uow.tasks.find_by_id.return_value = mock_task_model
        mock_verify_ownership.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
        task_update_data = TaskUpdate(title="Attempted Update")
        with pytest.raises(HTTPException) as exc_info:
            await task_service.update_task(
                task_id=mock_task_model.uuid,
                task_update=task_update_data,
                current_user=simple_user_internal
            )
        mock_uow.tasks.find_by_id.assert_called_once_with(mock_task_model.uuid)
        mock_verify_ownership.assert_called_once_with(simple_user_internal, mock_task_model.owner_uuid)
        mock_uow.commit.assert_not_called()
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "You do not have permission to access this resource."

    async def test_delete_task_success(
            self,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            mock_task_model: AsyncMock,
            simple_user_internal: UserInternal,
    ):
        """Test case for successful task deletion."""

        mock_uow.tasks.find_by_id.return_value = mock_task_model
        await task_service.delete_task(mock_task_model.uuid, simple_user_internal)
        mock_uow.tasks.find_by_id.assert_called_once_with(mock_task_model.uuid)
        mock_uow.tasks.delete.assert_called_once_with(mock_task_model)
        mock_uow.commit.assert_called_once()

    async def test_delete_task_not_found(
            self,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            simple_user_internal: UserInternal,
    ):
        """Test case for task not found during deletion."""

        mock_uow.tasks.find_by_id.return_value = None
        some_uuid = uuid4()
        with pytest.raises(HTTPException) as exc_info:
            await task_service.delete_task(some_uuid, simple_user_internal)
        mock_uow.tasks.find_by_id.assert_called_once_with(some_uuid)
        mock_uow.tasks.delete.assert_not_called()
        mock_uow.commit.assert_not_called()
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Task not found"

    @patch('src.services.task_service.verify_ownership')
    async def test_delete_task_permission_denied(
            self,
            mock_verify_ownership: AsyncMock,
            task_service: TaskService,
            mock_uow: IUnitOfWork,
            mock_task_model: AsyncMock,
            simple_user_internal: UserInternal,
    ):
        """Test case for permission denied when deleting a task."""

        mock_uow.tasks.find_by_id.return_value = mock_task_model
        mock_verify_ownership.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
        with pytest.raises(HTTPException) as exc_info:
            await task_service.delete_task(mock_task_model.uuid, simple_user_internal)
        mock_uow.tasks.find_by_id.assert_called_once_with(mock_task_model.uuid)
        mock_verify_ownership.assert_called_once_with(simple_user_internal, mock_task_model.owner_uuid)
        mock_uow.tasks.delete.assert_not_called()
        mock_uow.commit.assert_not_called()
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "You do not have permission to access this resource."
