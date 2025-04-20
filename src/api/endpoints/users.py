from typing import Annotated

from fastapi import Depends, APIRouter

from src.api.dependencies.user_dependency import get_current_user
from src.api.schemas.user import UserFromDB

user_router = APIRouter(
    prefix="/api/v1",
    tags=["Users"]
)


@user_router.get("/users/about_me/", response_model=UserFromDB)
async def read_user(current_user: Annotated[UserFromDB, Depends(get_current_user)]) -> UserFromDB:
    return current_user
