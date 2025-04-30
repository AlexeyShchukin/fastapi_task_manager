from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from src.api.schemas.user import UserFromDB
from src.core.security import oauth2_scheme, decode_token
from src.services.user_service import UserService
from src.utils.unit_of_work import IUnitOfWork, UnitOfWork


async def get_user_service(uow: Annotated[IUnitOfWork, Depends(UnitOfWork)]) -> UserService:
    return UserService(uow)


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserFromDB:
    payload = decode_token(token)
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await user_service.find_user_by_id(user_id)
    return user
