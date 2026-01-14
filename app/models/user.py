import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: str = Field(index=True)
    is_active: bool = Field(default=True)
    hashed_password: str = Field()

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
        )
    )
