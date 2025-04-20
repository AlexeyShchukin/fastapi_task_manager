from sqlalchemy import select

from src.db.models import User
from src.repositories.base_repository import Repository


class UserRepository(Repository):
    model = User

    async def find_by_name(self, username: str):
        stmt = select(self.model).where(self.model.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
