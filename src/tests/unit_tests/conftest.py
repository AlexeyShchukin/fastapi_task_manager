import types
from datetime import timezone, datetime, timedelta

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import Request, Response

from src.api.schemas.role import RoleSchema, PermissionSchema
from src.api.schemas.task import TaskCreate
from src.api.schemas.user import UserPublic, UserInternal, UserCreate
from src.db.models import Role, RefreshToken
from src.repositories.role_repository import RoleRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.services.task_service import TaskService
from src.services.token_service import TokenService
from src.services.user_service import UserService
from src.utils.unit_of_work import IUnitOfWork


@pytest.fixture
def create_mock_permission():
    """
    Fixture factory to create mock permission objects using SimpleNamespace.
    Returns a callable that takes id (int) and name (str) and returns a SimpleNamespace.
    """
    def _create_perm(id: int, name: str):
        return types.SimpleNamespace(id=id, name=name)
    return _create_perm


@pytest.fixture
def mock_uow():
    """
    Fixture to provide a mock UnitOfWork for testing.
    """
    uow_mock = AsyncMock()

    uow_mock.users = AsyncMock(spec=UserRepository)
    uow_mock.users.find_by_name = AsyncMock(return_value=None)
    uow_mock.users.add_one = AsyncMock()
    uow_mock.users.assign_role = AsyncMock()

    uow_mock.roles = AsyncMock(spec=RoleRepository)
    uow_mock.roles.find_by_name = AsyncMock()

    uow_mock.tasks = AsyncMock(spec=TaskRepository)

    uow_mock.refresh_tokens = AsyncMock(spec=RefreshTokenRepository)

    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()
    uow_mock.__aenter__.return_value = uow_mock
    uow_mock.__aexit__.return_value = None

    return uow_mock


@pytest.fixture
def task_service(mock_uow: IUnitOfWork):
    """
    Fixture to provide an instance of TaskService with a mock UoW.
    """
    return TaskService(uow=mock_uow)


@pytest.fixture
def user_service(mock_uow: IUnitOfWork) -> UserService:
    """
    Fixture to provide an instance of UserService with a mock UoW.
    """
    return UserService(uow=mock_uow)


@pytest.fixture
def sample_user_create() -> UserCreate:
    """
    Provides a sample UserCreate object.
    """
    return UserCreate(
        username="newuser",
        email="new@example.com",
        password="StrongPassword123!"
    )


@pytest.fixture
def sample_user_public() -> UserPublic:
    """
    Fixture to provide a sample UserPublic object.
    """
    return UserPublic(
        uuid=uuid4(),
        username="testuser",
        email="test@example.com"
    )


@pytest.fixture
def sample_password() -> str:
    """
    Provides a sample plain password.
    """
    return "TestPassword123!"



@pytest.fixture
def sample_hashed_password(sample_password: str) -> str:
    """
    Provides a sample hashed password.
    """
    # Using the actual hashing function for consistency in test data
    from src.core.security import hash_password
    return hash_password(sample_password)

@pytest.fixture
def mock_user_model(sample_user_public: UserPublic, sample_hashed_password: str):
    """
    Provides a mock SQLAlchemy User model instance.
    """
    mock = AsyncMock()
    mock.uuid = sample_user_public.uuid
    mock.username = sample_user_public.username
    mock.email = sample_user_public.email
    mock.hashed_password = sample_hashed_password
    mock.roles = []
    mock.permissions = []
    return mock

@pytest.fixture
def mock_role_model():
    """
    Provides a mock SQLAlchemy Role model instance for a default role.
    """
    mock = AsyncMock()
    mock.id = 1
    mock.name = "user"
    mock.permissions = []
    return mock

@pytest.fixture
def mock_admin_role_model():
    """
    Provides a mock SQLAlchemy Role model instance for an admin role.
    """
    mock = AsyncMock()
    mock.id = 2
    mock.name = "admin"
    # Mock permission objects, not just names
    mock.permissions = [AsyncMock(id=1, name="read"), AsyncMock(id=2, name="write")]
    return mock


@pytest.fixture
def sample_user_internal(
        mock_user_model: AsyncMock,
        sample_user_public: UserPublic
) -> UserInternal:
    """
    Fixture to provide a sample UserInternal object with roles and permissions.
    This fixture is responsible for setting up all necessary mocks for roles and permissions.
    """
    mock_user_model.uuid = sample_user_public.uuid
    mock_user_model.username = sample_user_public.username
    mock_user_model.email = sample_user_public.email
    mock_user_model.hashed_password = "hashed_password_for_user"

    mock_role_user = MagicMock(spec=Role)
    mock_role_user.id = 1
    mock_role_user.name = "user"
    mock_role_user.permissions = [
        types.SimpleNamespace(id=101, name="read_self_data"),
        types.SimpleNamespace(id=102, name="update_self_profile"),
    ]

    mock_role_admin = MagicMock(spec=Role)
    mock_role_admin.id = 2
    mock_role_admin.name = "admin"
    mock_role_admin.permissions = [
        types.SimpleNamespace(id=201, name="read_all_users"),
        types.SimpleNamespace(id=202, name="manage_roles"),
    ]

    mock_user_model.roles = [mock_role_user, mock_role_admin]

    roles_schema = [RoleSchema(id=r.id, name=r.name) for r in mock_user_model.roles]

    unique_permissions_dict = {}
    for role in mock_user_model.roles:
        for perm in role.permissions:
            if hasattr(perm, 'id') and hasattr(perm, 'name'):
                unique_permissions_dict[perm.id] = perm

    final_permissions_schema = [
        PermissionSchema(id=p.id, name=p.name) for p in unique_permissions_dict.values()
    ]

    return UserInternal(
        uuid=mock_user_model.uuid,
        username=mock_user_model.username,
        email=mock_user_model.email,
        hashed_password=mock_user_model.hashed_password,
        roles=roles_schema,
        permissions=final_permissions_schema,
        scope=None,
        cached_permission_names=None
    )


@pytest.fixture
def simple_user_internal(sample_user_public: UserPublic) -> UserInternal:
    """
    Fixture to provide a sample UserInternal object.
    """
    return UserInternal(
        uuid=sample_user_public.uuid,
        username=sample_user_public.username,
        email=sample_user_public.email,
        hashed_password="hashedpassword",
        roles=[],
        permissions=[],
        scope=None
    )


@pytest.fixture
def sample_task_create() -> TaskCreate:
    """
    Fixture to provide a sample TaskCreate object.
    """
    return TaskCreate(
        title="Test Task",
        description="This is a test description."
    )


@pytest.fixture
def mock_task_model(sample_user_public: UserPublic):
    """
    Fixture to provide a mock SQLAlchemy Task model instance.
    """
    mock = AsyncMock()
    mock.uuid = uuid4()
    mock.title = "Test Task"
    mock.description = "This is a test description."
    mock.completed = False
    mock.created_at = datetime.now(timezone.utc)
    mock.owner_uuid = sample_user_public.uuid
    return mock


@pytest.fixture
def token_service(mock_uow: IUnitOfWork) -> TokenService:
    """
    Fixture to provide a TokenService instance for testing.
    """
    return TokenService(uow=mock_uow)


@pytest.fixture
def mock_request() -> AsyncMock:
    """
    Fixture to provide a mock Request object.
    """
    mock = AsyncMock(spec=Request)
    mock.client = MagicMock()
    mock.client.host = "127.0.0.1"
    mock.headers = {"user-agent": "test-agent"}
    return mock


@pytest.fixture
def mock_response() -> AsyncMock:
    """
    Fixture to provide a mock Response object.
    """
    mock = AsyncMock(spec=Response)
    mock.headers = {}
    return mock


@pytest.fixture
def sample_refresh_token_obj(sample_user_internal: MagicMock) -> RefreshToken:
    """
    Fixture to provide a sample RefreshToken database object.
    """
    return RefreshToken(
        uuid=uuid4(),
        token="some_refresh_token_string",
        user_uuid=sample_user_internal.uuid,
        ip_address="127.0.0.1",
        user_agent="test-agent",
        created_at=datetime.now(timezone.utc) - timedelta(days=1),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        used=False,
        used_at=None
    )
