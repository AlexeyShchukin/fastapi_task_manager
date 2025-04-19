from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies.user_dependency import get_user_service, get_user_from_token
from src.api.schemas.token import TokenPairResponse, AccessTokenResponse
from src.api.schemas.user import UserFromDB, UserCreate
from src.core.security import create_access_token, create_refresh_token
from src.services.user_service import UserService

user_router = APIRouter(
    prefix="/api/v1",
    tags=["Users"]
)


@user_router.post("/register/", response_model=UserFromDB)
async def create_user(
        user_data: UserCreate,
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserFromDB:
    return await user_service.add_user(user_data)


@user_router.post(
    "/login",
    description="Creating access and refresh tokens",
    response_model=TokenPairResponse
)
async def login(
        user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> TokenPairResponse:
    await user_service.authenticate_user(user_data.username, user_data.password)
    access_token = create_access_token({"sub": user_data.username})
    refresh_token = create_refresh_token({"sub": user_data.username})
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


@user_router.get("/about_me/", response_model=UserFromDB)
async def read_user(current_user: Annotated[UserFromDB, Depends(get_user_from_token)]) -> UserFromDB:
    return current_user


@user_router.get(
    "/refresh",
    description="Creates a new access token based on the refresh token",
    response_model=AccessTokenResponse
)
def refresh(user: Annotated[UserFromDB, Depends(get_user_from_token)]) -> AccessTokenResponse:
    new_access_token = create_access_token({"sub": user.username})
    return AccessTokenResponse(access_token=new_access_token)
