from uuid import UUID

from fastapi import HTTPException, status
from redis.asyncio import Redis

from src.api.schemas.user import UserCreate, UserFromDB, UserInDB
from src.core.security import hash_password, verify_password
from src.services.rate_limiter import LoginRateLimiter
from src.utils.unit_of_work import IUnitOfWork


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, user: UserCreate) -> UserFromDB:
        async with self.uow as uow:
            if not await uow.users.find_by_name(user.username):
                hashed_password = hash_password(user.password)
                user_dict = user.model_dump(exclude={"password"})
                user_dict["hashed_password"] = hashed_password
                user_from_db = await uow.users.add_one(user_dict)
                user_to_return = UserFromDB.model_validate(user_from_db)
                await uow.commit()
                return user_to_return
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this name already exists"
            )

    async def find_user_by_name(self, username: str) -> UserInDB:
        async with self.uow as uow:
            user = await uow.users.find_by_name(username)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return UserInDB.model_validate(user)

    async def authenticate_user(self, username: str, password: str, redis: Redis) -> UserFromDB:
        limiter = LoginRateLimiter(redis)

        if await limiter.is_blocked(username):
            raise HTTPException(
                status_code=403,
                detail="Too many login attempts. Try again later."
            )

        user = await self.find_user_by_name(username)

        if not verify_password(password, user.hashed_password):
            attempts = await limiter.incr_attempts(username)
            remaining = limiter.max_attempts - attempts
            if remaining > 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid password. {remaining} login attempts remaining.",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Too many failed login attempts. You are temporarily blocked.",
                    headers={"WWW-Authenticate": "Bearer"}
                )

        await limiter.reset_attempts(username)
        return user

    async def find_user_by_id(self, user_id: UUID) -> UserInDB:
        async with self.uow as uow:
            user = await uow.users.find_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return UserInDB.model_validate(user)
