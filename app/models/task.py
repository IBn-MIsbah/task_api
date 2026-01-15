import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, index=True, primary_key=True)
    title: str = Field(nullable=False)
    description: str = Field()
    status: str = Field(default="pending")
    priority: str = Field(default="medium")
    due_date: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True)))
    user_id: UUID = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="tasks")

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
        )
    )
