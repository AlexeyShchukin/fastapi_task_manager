from datetime import timezone, datetime
from typing import Annotated
from uuid import UUID, uuid4

from redis.asyncio import Redis
from fastapi import Depends, APIRouter, Request, status, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies.token_dependency import get_token_service
from src.api.dependencies.user_dependency import get_user_service, get_current_user
from src.api.schemas.token import AccessTokenResponse, SessionInfo
from src.api.schemas.user import UserFromDB, UserCreate
from src.core.redis import get_redis
from src.core.security import create_access_token, decode_token
from src.services.token_service import TokenService
from src.services.user_service import UserService

auth_router = APIRouter(
    prefix="/api/v1",
    tags=["Auth"]
)


@auth_router.post(
    "/auth/register/",
    response_model=UserFromDB,
    status_code=status.HTTP_201_CREATED,
    description="Register a new user",
    responses={
        201: {"description": "User successfully registered"},
        400: {"description": "A user with this name already exists"}
    }
)
async def create_user(
        user_data: UserCreate,
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserFromDB:
    return await user_service.add_user(user_data)


@auth_router.post(
    "/auth/login/",
    description="Creating access and refresh tokens",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User successfully logged in"},
        404: {"description": "User not found"},
        401: {"description": "Invalid password"},
        403: {"description": "Too many login attempts"}
    }
)
async def login(
        user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_service: Annotated[UserService, Depends(get_user_service)],
        token_service: Annotated[TokenService, Depends(get_token_service)],
        redis: Annotated[Redis, Depends(get_redis)],
        request: Request,
        response: Response
) -> AccessTokenResponse:
    user = await user_service.authenticate_user(user_data.username, user_data.password, redis)

    access_token = create_access_token(
        {"sub": str(user.uuid),
         "iat": datetime.now(timezone.utc),
         "jti": str(uuid4())
         }
    )
    await token_service.issue_new_refresh_token(user.uuid, response, request)
    return AccessTokenResponse(access_token=access_token)


@auth_router.post(
    "/auth/refresh/",
    description="Issue new access token and rotate refresh token",
    response_model=AccessTokenResponse
)
async def refresh(
        request: Request,
        response: Response,
        token_service: Annotated[TokenService, Depends(get_token_service)],
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> AccessTokenResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_token(refresh_token)
    try:
        user_id: UUID = UUID(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    await user_service.find_user_by_id(user_id)
    return await token_service.rotate_tokens(user_id, refresh_token, response, request)


@auth_router.get("/auth/sessions/", response_model=list[SessionInfo])
async def get_user_sessions(
        token_service: Annotated[TokenService, Depends(get_token_service)],
        current_user: Annotated[UserFromDB, Depends(get_current_user)]
):
    return await token_service.get_user_sessions(current_user.uuid)


@auth_router.post(
    "/auth/logout/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "The session logged out"}})
async def logout_session(
        request: Request,
        response: Response,
        current_user: Annotated[UserFromDB, Depends(get_current_user)],
        token_service: Annotated[TokenService, Depends(get_token_service)],
):
    refresh_token = request.cookies.get("refresh_token")
    await token_service.logout_one(current_user.uuid, refresh_token)
    response.delete_cookie("refresh_token")


@auth_router.post(
    "/auth/logout_all/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "All sessions logged out"}}
)
async def logout_all_sessions(
        response: Response,
        current_user: Annotated[UserFromDB, Depends(get_current_user)],
        token_service: Annotated[TokenService, Depends(get_token_service)]
):
    await token_service.logout_all(current_user.uuid)
    response.delete_cookie("refresh_token")
