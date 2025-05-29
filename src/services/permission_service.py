import json
from uuid import UUID

from fastapi import HTTPException, Depends

from src.api.dependencies.user_dependency import get_current_user
from src.api.schemas.user import UserInternal
from src.core.redis import get_redis


def has_permission(user_permissions: set[str], resource: str, action: str, scope: str) -> bool:
    if scope:
        target_permission = f"{resource}:{action}:{scope}"
        if target_permission in user_permissions:
            return True

    target_permission_no_scope = f"{resource}:{action}"
    return target_permission_no_scope in user_permissions


def verify_ownership(user: UserInternal, resource_owner_id: UUID) -> None:
    """Raises 403 if user's scope is 'own' and user is not the resource owner."""
    if getattr(user, "scope", None) == "own" and user.uuid != resource_owner_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this resource"
        )


async def get_user_with_cached_permissions(
    user: UserInternal = Depends(get_current_user),
    redis=Depends(get_redis),
    ttl: int = 300,
) -> UserInternal:
    """
    Returns a set of user permissions, first trying from Redis,
    on failure - from the DB and puts in Redis for ttl seconds.
    """
    key = f"perm:{user.uuid}"
    data = await redis.get(key)
    if data:
        perms = set(json.loads(data))
    else:
        perms = user.permission_names
        await redis.set(key, json.dumps(list(perms)), ex=ttl)

    user.cached_permission_names = perms
    return user