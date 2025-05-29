from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.api.schemas.user import UserInternal
from src.services.permission_service import has_permission, get_user_with_cached_permissions


def permission_required(resource: str, action: str, allow_own: bool = False):
    async def checker(
            user: Annotated[UserInternal, Depends(get_user_with_cached_permissions)]
    ) -> UserInternal:

        user_permissions = user.cached_permission_names

        if has_permission(user_permissions, resource, action, "any"):
            return user

        if allow_own and has_permission(user_permissions, resource, action, "own"):
            user.scope = "own"
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    return checker
