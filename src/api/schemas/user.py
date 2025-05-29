from re import search
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, constr, Field, field_validator

from src.api.schemas.role import PermissionSchema, RoleSchema


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: constr(min_length=3,
                     max_length=20) = Field(description="Username must be between 3 and 20 characters long")
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=8) = Field(
        description="""Password must be at least 8 characters long and include at least one uppercase letter, 
        one lowercase letter, one digit, and one special character. Spaces are not allowed."""
    )


    @field_validator('password')
    @classmethod
    def password_strength(cls, pwd) -> str:
        if not search(r'[A-Z]', pwd):
            raise ValueError('The password must contain at least one capital letter.')
        if not search(r'[a-z]', pwd):
            raise ValueError('The password must contain at least one lowercase letter.')
        if not search(r'[0-9]', pwd):
            raise ValueError('The password must contain at least one number.')
        if not search(r'[^A-Za-z0-9]', pwd):
            raise ValueError('The password must contain at least one special character.')
        if search(r'\s', pwd):
            raise ValueError('The password cannot contain spaces.')
        return pwd


class UserPublic(UserBase):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID


class UserInternal(UserPublic):
    hashed_password: str
    roles: list[RoleSchema]
    permissions: list[PermissionSchema]
    scope: str | None = None
    cached_permission_names: set[str] | None = None

    @property
    def permission_names(self) -> set[str]:
        return {p.name for p in self.permissions}
