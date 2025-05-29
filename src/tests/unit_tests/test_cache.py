import json
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from src.api.schemas.role import PermissionSchema
from src.api.schemas.user import UserInternal
from src.services.permission_service import get_user_with_cached_permissions


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_user_with_cached_permissions_from_cache():
    user = UserInternal(
        uuid=uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        roles=[],
        permissions=[
            PermissionSchema(id=1, name="task:read:any"),
            PermissionSchema(id=2, name="user:update:own"),
        ],
        cached_permission_names=None,
        scope=None,
    )
    redis_mock = AsyncMock()
    redis_mock.get.return_value = json.dumps(["task:read:any", "user:update:own"])

    result_user = await get_user_with_cached_permissions(user=user, redis=redis_mock)

    assert result_user.cached_permission_names == {"task:read:any", "user:update:own"}
    redis_mock.get.assert_called_once()
    redis_mock.set.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_user_with_cached_permissions_from_db():
    user = UserInternal(
        uuid=uuid4(),
        username="dbuser",
        email="dbuser@example.com",
        hashed_password="hashed_db",
        roles=[],
        permissions=[
            PermissionSchema(id=3, name="user:read:any"),
        ],
        cached_permission_names=None,
        scope=None,
    )
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None

    result_user = await get_user_with_cached_permissions(user=user, redis=redis_mock)

    assert result_user.cached_permission_names == {"user:read:any"}
    redis_mock.set.assert_called_once()
