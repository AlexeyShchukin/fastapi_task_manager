from uuid import UUID

from sqlalchemy import select

from src.db.models import RefreshToken
from src.repositories.base_repository import Repository


class RefreshTokenRepository(Repository):
    model = RefreshToken

    # async def find_token(self, token: str) -> RefreshToken | None:
    #     stmt = select(self.model).where(self.model.token == token)
    #     result = await self.session.execute(stmt)
    #     return result.scalar_one_or_none()
    #
    # async def delete_token(self, token: str):
    #     token_obj = await self.find_token(token)
    #     if token_obj:
    #         await self.session.delete(token_obj)
    #
    # async def delete_all_for_user(self, user_id: UUID):
    #     stmt = select(self.model).where(self.model.user_uuid == user_id)
    #     result = await self.session.execute(stmt)
    #     tokens = result.scalars().all()
    #     for token in tokens:
    #         await self.session.delete(token)
