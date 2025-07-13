import types

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from redis.asyncio import Redis

from src.api.schemas.role import PermissionSchema, RoleSchema
from src.api.schemas.user import UserCreate, UserPublic, UserInternal
from src.db.models import User

from src.services.user_service import UserService
from src.utils.unit_of_work import IUnitOfWork


class TestUserService:
    """
    Unit tests for the UserService.
    """

    @patch('src.services.user_service.hash_password')
    async def test_add_user_success(
            self,
            mock_hash_password: AsyncMock,
            user_service: UserService,
            mock_uow: IUnitOfWork,
            sample_user_create: UserCreate,
            mock_role_model: AsyncMock
    ):
        """
        Tests successful user creation and default role assignment.
        """

        hashed_password_mock = "hashed_password_mock"
        mock_hash_password.return_value = hashed_password_mock

        mock_user_db_instance = MagicMock(spec=User)
        mock_user_db_instance.uuid = uuid4()
        mock_user_db_instance.username = sample_user_create.username
        mock_user_db_instance.email = sample_user_create.email
        mock_user_db_instance.hashed_password = hashed_password_mock
        mock_user_db_instance.roles = []

        mock_uow.users.add_one.return_value = mock_user_db_instance

        mock_uow.roles.find_by_name.return_value = mock_role_model
        mock_uow.users.assign_role = AsyncMock()

        result = await user_service.add_user(sample_user_create)

        mock_uow.users.find_by_name.assert_called_once_with(sample_user_create.username)
        mock_hash_password.assert_called_once_with(sample_user_create.password)

        assert result.username == sample_user_create.username
        assert result.email == sample_user_create.email
        assert result.uuid == mock_user_db_instance.uuid

    async def test_add_user_already_exists(
            self,
            user_service: UserService,
            mock_uow: IUnitOfWork,
            sample_user_create: UserCreate,
            mock_user_model: AsyncMock
    ):
        """
        Tests user creation failure when username already exists.
        """
        mock_uow.users.find_by_name.return_value = mock_user_model
        with pytest.raises(HTTPException) as exc_info:
            await user_service.add_user(sample_user_create)

        mock_uow.users.find_by_name.assert_called_once_with(sample_user_create.username)
        mock_uow.users.add_one.assert_not_called()
        mock_uow.commit.assert_not_called()
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "A user with this name already exists"

    async def test_add_user_default_role_not_found(
            self,
            user_service: UserService,
            mock_uow: IUnitOfWork,
            sample_user_create: UserCreate,
            mock_user_model: AsyncMock
    ):
        """
        Tests user creation failure when default role is not found.
        """
        mock_uow.users.find_by_name.return_value = None
        mock_uow.users.add_one.return_value = mock_user_model
        mock_uow.roles.find_by_name.return_value = None
        mock_uow.users.assign_role = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await user_service.add_user(sample_user_create)

        mock_uow.users.find_by_name.assert_called_once_with(sample_user_create.username)
        mock_uow.users.add_one.assert_called_once()
        mock_uow.roles.find_by_name.assert_called_once_with("user")
        mock_uow.users.assign_role.assert_not_called()
        mock_uow.commit.assert_not_called()
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Default role not found"

    async def test_find_user_by_name_success(
            self,
            user_service: UserService,
            mock_uow: IUnitOfWork,
            sample_user_public: UserPublic,
            mock_user_model: AsyncMock,
            mock_role_model: MagicMock,
            mock_admin_role_model: MagicMock,
            create_mock_permission
    ):
        """
        Tests successful retrieval of a user by username with roles and permissions.
        """
        mock_role_model.id = 1
        mock_role_model.name = "user"

        mock_role_model.permissions = [
            create_mock_permission(id=101, name="read_self_data"),
            create_mock_permission(id=102, name="update_self_profile")
        ]

        mock_admin_role_model.id = 2
        mock_admin_role_model.name = "admin"
        mock_admin_role_model.permissions = [
            create_mock_permission(id=201, name="read_all_users"),
            create_mock_permission(id=202, name="manage_roles")
        ]

        mock_user_model.roles = [mock_role_model, mock_admin_role_model]

        mock_uow.users.find_by_name.return_value = mock_user_model

        mock_user_model.uuid = sample_user_public.uuid
        mock_user_model.username = sample_user_public.username
        mock_user_model.email = sample_user_public.email
        mock_user_model.hashed_password = "hashed_password_for_user"

        result = await user_service.find_user_by_name(sample_user_public.username)

        mock_uow.users.find_by_name.assert_called_once_with(sample_user_public.username)

        assert result.username == sample_user_public.username
        assert result.email == sample_user_public.email
        assert result.uuid == sample_user_public.uuid

        assert len(result.roles) == 2
        role_names = {r.name for r in result.roles}
        assert "user" in role_names
        assert "admin" in role_names
        assert all(isinstance(r, RoleSchema) for r in result.roles)

        assert len(result.permissions) == 4
        permission_names = {p.name for p in result.permissions}
        assert "read_self_data" in permission_names
        assert "update_self_profile" in permission_names
        assert "read_all_users" in permission_names
        assert "manage_roles" in permission_names
        assert all(isinstance(p, PermissionSchema) for p in result.permissions)

        assert isinstance(result, UserInternal)

    async def test_find_user_by_name_not_found(
            self,
            user_service: UserService,
            mock_uow: IUnitOfWork,
            sample_user_public: UserPublic
    ):
        """
        Tests user not found when searching by username.
        """
        mock_uow.users.find_by_name.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await user_service.find_user_by_name(sample_user_public.username)

        mock_uow.users.find_by_name.assert_called_once_with(sample_user_public.username)
        mock_uow.commit.assert_not_called()
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "User not found"

    async def test_find_user_by_id_success(
            self,
            user_service: UserService,
            mock_uow: IUnitOfWork,
            sample_user_public: UserPublic,
            mock_user_model: AsyncMock,
            mock_role_model: AsyncMock,
            mock_admin_role_model: AsyncMock,
            create_mock_permission
    ):
        """
        Tests successful retrieval of a user by id with roles and permissions.
        """
        mock_role_model.id = 1
        mock_role_model.name = "user"

        mock_role_model.permissions = [
            create_mock_permission(id=101, name="read_self_data"),
            create_mock_permission(id=102, name="update_self_profile")
        ]

        mock_admin_role_model.id = 2
        mock_admin_role_model.name = "admin"

        mock_admin_role_model.permissions = [
            create_mock_permission(id=201, name="read_all_users"),
            create_mock_permission(id=202, name="manage_roles")
        ]

        mock_user_model.roles = [mock_role_model, mock_admin_role_model]

        mock_uow.users.find_by_id.return_value = mock_user_model

        mock_user_model.uuid = sample_user_public.uuid
        mock_user_model.username = sample_user_public.username
        mock_user_model.email = sample_user_public.email
        mock_user_model.hashed_password = "hashed_password_for_user"

        result = await user_service.find_user_by_id(sample_user_public.uuid)

        mock_uow.users.find_by_id.assert_called_once_with(sample_user_public.uuid)

        assert result.username == sample_user_public.username
        assert result.email == sample_user_public.email
        assert result.uuid == sample_user_public.uuid

        assert len(result.roles) == 2
        role_names = {r.name for r in result.roles}
        assert "user" in role_names
        assert "admin" in role_names
        assert all(isinstance(r, RoleSchema) for r in result.roles)

        assert len(result.permissions) == 4
        permission_names = {p.name for p in result.permissions}
        assert "read_self_data" in permission_names
        assert "update_self_profile" in permission_names
        assert "read_all_users" in permission_names
        assert "manage_roles" in permission_names
        assert all(isinstance(p, PermissionSchema) for p in result.permissions)

        assert isinstance(result, UserInternal)

    async def test_find_user_by_id_not_found(
            self,
            user_service: UserService,
            mock_uow: IUnitOfWork,
    ):
        """
        Tests user not found when searching by UUID.
        """
        mock_uow.users.find_by_id.return_value = None
        some_uuid = uuid4()
        with pytest.raises(HTTPException) as exc_info:
            await user_service.find_user_by_id(some_uuid)

        mock_uow.users.find_by_id.assert_called_once_with(some_uuid)
        mock_uow.commit.assert_not_called()
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "User not found"

    @patch('src.services.user_service.verify_password')
    @patch('src.services.user_service.LoginRateLimiter')
    async def test_authenticate_user_success(
            self,
            mock_login_rate_limiter_cls: AsyncMock,
            mock_verify_password: AsyncMock,
            user_service: UserService,
            sample_user_internal: UserInternal,
            sample_password: str,
    ):
        """
        Tests successful user authentication.
        """
        mock_limiter_instance = AsyncMock()
        mock_login_rate_limiter_cls.return_value = mock_limiter_instance
        mock_limiter_instance.is_blocked.return_value = False
        mock_verify_password.return_value = True
        mock_limiter_instance.reset_attempts = AsyncMock()

        with patch.object(user_service, 'find_user_by_name',
                          return_value=sample_user_internal) as mock_find_user_by_name:
            result = await user_service.authenticate_user(sample_user_internal.username, sample_password,
                                                          AsyncMock(spec=Redis))

            mock_login_rate_limiter_cls.assert_called_once()
            mock_limiter_instance.is_blocked.assert_called_once_with(sample_user_internal.username)
            mock_find_user_by_name.assert_called_once_with(sample_user_internal.username)
            mock_verify_password.assert_called_once_with(sample_password, sample_user_internal.hashed_password)
            mock_limiter_instance.reset_attempts.assert_called_once_with(sample_user_internal.username)
            assert isinstance(result, UserInternal)
            assert result.username == sample_user_internal.username

    @patch('src.services.user_service.LoginRateLimiter')
    async def test_authenticate_user_blocked(
            self,
            mock_login_rate_limiter_cls: AsyncMock,
            user_service: UserService,
            sample_user_internal: UserInternal,
            sample_password: str,
    ):
        """
        Tests user authentication failure when user is blocked by rate limiter.
        """
        mock_limiter_instance = AsyncMock()
        mock_login_rate_limiter_cls.return_value = mock_limiter_instance
        mock_limiter_instance.is_blocked.return_value = True

        with pytest.raises(HTTPException) as exc_info:
            await user_service.authenticate_user(sample_user_internal.username, sample_password, AsyncMock(spec=Redis))

        mock_login_rate_limiter_cls.assert_called_once()
        mock_limiter_instance.is_blocked.assert_called_once_with(sample_user_internal.username)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Too many login attempts. Try again later."

    @patch('src.services.user_service.verify_password')
    @patch('src.services.user_service.LoginRateLimiter')
    async def test_authenticate_user_invalid_password_remaining_attempts(
            self,
            mock_login_rate_limiter_cls: AsyncMock,
            mock_verify_password: AsyncMock,
            user_service: UserService,
            sample_user_internal: UserInternal,
            sample_password: str,
    ):
        """
        Tests user authentication failure with invalid password and remaining attempts.
        """
        mock_limiter_instance = AsyncMock()
        mock_login_rate_limiter_cls.return_value = mock_limiter_instance
        mock_limiter_instance.is_blocked.return_value = False
        mock_verify_password.return_value = False
        mock_limiter_instance.incr_attempts.return_value = 1
        mock_limiter_instance.max_attempts = 3

        with patch.object(user_service, 'find_user_by_name',
                          return_value=sample_user_internal) as mock_find_user_by_name:
            with pytest.raises(HTTPException) as exc_info:
                await user_service.authenticate_user(sample_user_internal.username, sample_password,
                                                     AsyncMock(spec=Redis))

            mock_limiter_instance.is_blocked.assert_called_once_with(sample_user_internal.username)
            mock_find_user_by_name.assert_called_once_with(sample_user_internal.username)
            mock_verify_password.assert_called_once_with(sample_password, sample_user_internal.hashed_password)
            mock_limiter_instance.incr_attempts.assert_called_once_with(sample_user_internal.username)
            mock_limiter_instance.reset_attempts.assert_not_called()
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid password. 2 login attempts remaining."

    @patch('src.services.user_service.verify_password')
    @patch('src.services.user_service.LoginRateLimiter')
    async def test_authenticate_user_invalid_password_blocked_after_attempts(
            self,
            mock_login_rate_limiter_cls: AsyncMock,
            mock_verify_password: AsyncMock,
            user_service: UserService,
            sample_user_internal: UserInternal,
            sample_password: str,
    ):
        """
        Tests user authentication failure with invalid password leading to block.
        """
        mock_limiter_instance = AsyncMock()
        mock_login_rate_limiter_cls.return_value = mock_limiter_instance
        mock_limiter_instance.is_blocked.return_value = False
        mock_verify_password.return_value = False
        mock_limiter_instance.incr_attempts.return_value = 3
        mock_limiter_instance.max_attempts = 3

        with patch.object(user_service, 'find_user_by_name',
                          return_value=sample_user_internal) as mock_find_user_by_name:
            with pytest.raises(HTTPException) as exc_info:
                await user_service.authenticate_user(sample_user_internal.username, sample_password,
                                                     AsyncMock(spec=Redis))

            mock_limiter_instance.is_blocked.assert_called_once_with(sample_user_internal.username)
            mock_find_user_by_name.assert_called_once_with(sample_user_internal.username)
            mock_verify_password.assert_called_once_with(sample_password, sample_user_internal.hashed_password)
            mock_limiter_instance.incr_attempts.assert_called_once_with(sample_user_internal.username)
            mock_limiter_instance.reset_attempts.assert_not_called()
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert exc_info.value.detail == "Too many failed login attempts. You are temporarily blocked."

    @patch('src.services.user_service.verify_password')
    @patch('src.services.user_service.LoginRateLimiter')
    async def test_authenticate_user_not_found(
            self,
            mock_login_rate_limiter_cls: AsyncMock,
            mock_verify_password: AsyncMock,
            user_service: UserService,
            sample_user_internal: UserInternal,
            sample_password: str,
    ):
        """
        Tests user authentication failure when user is not found.
        """
        mock_limiter_instance = AsyncMock()
        mock_login_rate_limiter_cls.return_value = mock_limiter_instance
        mock_limiter_instance.is_blocked.return_value = False

        with patch.object(user_service, 'find_user_by_name',
                          side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                                    detail="User not found")) as mock_find_user_by_name:
            with pytest.raises(HTTPException) as exc_info:
                await user_service.authenticate_user(sample_user_internal.username, sample_password,
                                                     AsyncMock(spec=Redis))

            mock_limiter_instance.is_blocked.assert_called_once_with(sample_user_internal.username)
            mock_find_user_by_name.assert_called_once_with(sample_user_internal.username)
            mock_verify_password.assert_not_called()
            mock_limiter_instance.incr_attempts.assert_not_called()
            mock_limiter_instance.reset_attempts.assert_not_called()
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == "User not found"
