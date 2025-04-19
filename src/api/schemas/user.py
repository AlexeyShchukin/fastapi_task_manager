from re import search
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, constr, Field, field_validator


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: constr(min_length=3,
                     max_length=20) = Field(description="Username must be between 3 and 20 characters long")
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=8) = Field(description="""Password must be at least 8 characters long and include 
    at least one uppercase letter, one lowercase letter, one number, and one special character.""")

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
        return pwd


class UserFromDB(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserInDB(UserFromDB):
    uuid: UUID
    hashed_password: str
