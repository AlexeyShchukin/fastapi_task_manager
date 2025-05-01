from uuid import UUID

from fastapi import Request, HTTPException

from src.api.schemas.token import SessionInfo
from src.db.models import RefreshToken
from src.utils.request_utils import get_client_ip, get_user_agent
from src.utils.unit_of_work import IUnitOfWork


class TokenService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def save_refresh_token(self, user_uuid: UUID, token: str, request: Request) -> RefreshToken:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        refresh_token_data = {
            "token": token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "user_uuid": user_uuid
        }
        async with self.uow as uow:
            refresh_token = await self.uow.refresh_tokens.add_one(refresh_token_data)
            await uow.commit()
            return refresh_token

    async def get_user_sessions(self, user_uuid: UUID) -> list[SessionInfo]:
        async with self.uow:
            tokens = await self.uow.refresh_tokens.find_all_by_user(user_uuid)
            return [SessionInfo.model_validate(token) for token in tokens]

    async def get_refresh_token_from_db(self, user_id: UUID, refresh_token: str) -> RefreshToken | None:
        async with self.uow:
            token_obj = await self.uow.refresh_tokens.find_by_token_and_user(refresh_token, user_id)
            if token_obj is None:
                raise HTTPException(status_code=404, detail="Token not found")
            return token_obj

    async def logout_one(self, user_id: UUID, refresh_token: str):
        token_obj = await self.get_refresh_token_from_db(user_id, refresh_token)
        async with self.uow as uow:
            await uow.refresh_tokens.delete(token_obj)
            await uow.commit()

    async def logout_all(self, user_id: UUID) -> None:
        async with self.uow as uow:
            await uow.refresh_tokens.delete_all_for_user(user_id)
            await uow.commit()

    async def cleanup_expired_sessions(self):
        async with self.uow as uow:
            await uow.refresh_tokens.delete_expired_tokens()
            await uow.commit()

