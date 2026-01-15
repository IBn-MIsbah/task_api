import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.task import Task


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: str = Field(index=True)
    is_active: bool = Field(default=True)
    hashed_password: str = Field()

    tasks: List["Task"] = Relationship(back_populates="owner")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
        )
    )
