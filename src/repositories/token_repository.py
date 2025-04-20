from uuid import UUID

from sqlalchemy import select

from src.db.models import RefreshToken
from src.repositories.base_repository import Repository


class RefreshTokenRepository(Repository):
    model = RefreshToken

    async def find_all_by_user(self, user_uuid: UUID) -> list[RefreshToken]:
        stmt = select(self.model).where(self.model.user_uuid == user_uuid)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_token_and_user(self, token: str, user_id: UUID) -> RefreshToken | None:
        stmt = select(self.model).where(
            self.model.token == token,
            self.model.user_uuid == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, token_obj: RefreshToken):
        await self.session.delete(token_obj)

    async def delete_all_for_user(self, user_id: UUID):
        stmt = select(self.model).where(self.model.user_uuid == user_id)
        result = await self.session.execute(stmt)
        tokens = result.scalars().all()
        for token in tokens:
            await self.session.delete(token)
