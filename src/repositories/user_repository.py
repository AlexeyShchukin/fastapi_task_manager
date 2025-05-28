from uuid import UUID

from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload, selectinload

from src.db.models import User, users_roles, Role
from src.repositories.base_repository import Repository


class UserRepository(Repository):
    model = User

    async def find_by_name(self, username: str):
        stmt = (
            select(self.model)
            .where(self.model.username == username)
            .options(selectinload(self.model.roles)
                     .selectinload(Role.permissions)
                     )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, uuid_: UUID):
        stmt = (
            select(self.model)
            .where(self.model.uuid == uuid_)
            .options(selectinload(self.model.roles)
                     .selectinload(Role.permissions)
                     )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def assign_role(self, user_id: UUID, role_id: int) -> None:
        stmt = insert(users_roles).values(user_id=user_id, role_id=role_id)
        await self.session.execute(stmt)
