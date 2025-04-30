from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import DateTime, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import settings
from src.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    owner_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"), nullable=False)

    owner = relationship("User", back_populates="tasks")


class User(Base):
    __tablename__ = "users"

    uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)

    tasks = relationship("Task", back_populates="owner")
    token = relationship("RefreshToken", back_populates="user")


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        nullable=False)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(default=True)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"), nullable=False)

    user = relationship("User", back_populates="token")

    def __repr__(self):
        return f"<RefreshToken(user_id={self.user_uuid}, expires_at={self.expires_at})>"
