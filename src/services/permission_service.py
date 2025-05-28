from uuid import UUID

from fastapi import HTTPException

from src.api.schemas.user import UserInternal


def has_permission(user_permissions: set[str], resource: str, action: str, scope: str) -> bool:
    if scope:
        target_permission = f"{resource}:{action}:{scope}"
        if target_permission in user_permissions:
            return True

    target_permission_no_scope = f"{resource}:{action}"
    return target_permission_no_scope in user_permissions


def verify_ownership(user: UserInternal, resource_owner_id: UUID):
    if getattr(user, "scope", None) == "own" and user.uuid != resource_owner_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this resource"
        )
