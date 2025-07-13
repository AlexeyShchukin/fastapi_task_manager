import pytest
from uuid import uuid4

from fastapi import HTTPException

from src.api.dependencies.permission_dependency import permission_required
from src.api.schemas.role import PermissionSchema
from src.api.schemas.user import UserInternal
from src.services.permission_service import get_user_with_cached_permissions


@pytest.mark.asyncio
@pytest.mark.integration
async def test_permission_required_with_redis_get_redis(redis_client):

    test_uuid = uuid4()
    permissions = {"task:read:any", "task:create", "task:update:own"}

    user = UserInternal(
        uuid=test_uuid,
        username="cached_user",
        email="cached@example.com",
        hashed_password="hashed",
        roles=[],
        permissions=[PermissionSchema(id=1, name=p) for p in permissions],
        scope=None,
        cached_permission_names=set(),
    )

    redis_key = f"perm:{test_uuid}"
    await redis_client.delete(redis_key)

    user_with_cache = await get_user_with_cached_permissions(user=user, redis=redis_client)
    assert user_with_cache.cached_permission_names == permissions

    data = await redis_client.get(redis_key)
    assert data is not None
    assert set(eval(data)) == permissions

    user2 = UserInternal(
        uuid=test_uuid,
        username="cached_user",
        email="cached@example.com",
        hashed_password="hashed",
        roles=[],
        permissions=[],  # пусто
        scope=None,
        cached_permission_names=set(),
    )

    user2 = await get_user_with_cached_permissions(user=user2, redis=redis_client)
    assert "task:read:any" in user2.cached_permission_names

    checker = permission_required("task", "read")
    checked_user = await checker(user2)
    assert checked_user.uuid == test_uuid

    checker_fail = permission_required("task", "delete")
    with pytest.raises(HTTPException) as exc:
        await checker_fail(user2)
    assert exc.value.status_code == 403
