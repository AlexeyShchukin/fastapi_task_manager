from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.api.dependencies.user_dependency import get_current_user
from src.api.schemas.user import UserInternal
from src.services.permission_service import has_permission


def permission_required(resource: str, action: str, allow_own: bool = False):
    async def checker(user: Annotated[UserInternal, Depends(get_current_user)]) -> UserInternal :

        if has_permission(user.permission_names, resource, action, "any"):
            return user

        if allow_own and has_permission(user.permission_names, resource, action, "own"):
            user.scope = "own"
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    return checker
