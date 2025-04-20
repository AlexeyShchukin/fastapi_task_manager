from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import Depends, APIRouter, Request, status, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies.token_dependency import get_token_service
from src.api.dependencies.user_dependency import get_user_service, get_current_user
from src.api.schemas.token import TokenPairResponse, AccessTokenResponse, SessionInfo
from src.api.schemas.user import UserFromDB, UserCreate
from src.core.security import create_access_token, create_refresh_token, decode_token
from src.services.token_service import TokenService

from src.services.user_service import UserService

auth_router = APIRouter(
    prefix="/api/v1",
    tags=["Auth"]
)


@auth_router.post("/auth/register/", response_model=UserFromDB)
async def create_user(
        user_data: UserCreate,
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserFromDB:
    return await user_service.add_user(user_data)


@auth_router.post(
    "/auth/login/",
    description="Creating access and refresh tokens",
    response_model=TokenPairResponse
)
async def login(
        user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_service: Annotated[UserService, Depends(get_user_service)],
        token_service: Annotated[TokenService, Depends(get_token_service)],
        request: Request,
        response: Response
) -> TokenPairResponse:
    user = await user_service.authenticate_user(user_data.username, user_data.password)
    access_token = create_access_token({"sub": user_data.username})
    refresh_token = create_refresh_token({"sub": user_data.username})

    await token_service.save_refresh_token(user.uuid, refresh_token, request)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        max_age=int(timedelta(days=7).total_seconds()),
        expires=datetime.now(timezone.utc) + timedelta(days=7)
    )
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.get(
    "/auth/refresh/",
    description="Creates a new access token based on the refresh token",
    response_model=AccessTokenResponse
)
async def refresh(
        request: Request,
        token_service: Annotated[TokenService, Depends(get_token_service)],
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> AccessTokenResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_token(refresh_token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await user_service.find_user_by_name(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token_in_db = await token_service.get_refresh_token_from_db(user.uuid, refresh_token)
    if token_in_db is None:
        raise HTTPException(status_code=401, detail="Refresh token not recognized")

    new_access_token = create_access_token({"sub": user.username})
    return AccessTokenResponse(access_token=new_access_token)


@auth_router.get("/auth/sessions/", response_model=list[SessionInfo])
async def get_user_sessions(
        token_service: Annotated[TokenService, Depends(get_token_service)],
        current_user: Annotated[UserFromDB, Depends(get_current_user)]
):
    return await token_service.get_user_sessions(current_user.uuid)


@auth_router.post(
    "/auth/logout/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "The session logged out"}}
)
async def logout_session(
        request: Request,
        response: Response,
        current_user: Annotated[UserFromDB, Depends(get_current_user)],
        token_service: Annotated[TokenService, Depends(get_token_service)],
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token missing")
    await token_service.logout_one(current_user.uuid, refresh_token)
    response.delete_cookie("refresh_token")


@auth_router.post(
    "/auth/logout_all/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "All sessions logged out"}}
)
async def logout_all_sessions(
        current_user: Annotated[UserFromDB, Depends(get_current_user)],
        token_service: Annotated[TokenService, Depends(get_token_service)]
):
    await token_service.logout_all(current_user.uuid)
