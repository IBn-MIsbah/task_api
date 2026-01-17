import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

import sqlalchemy as sq
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class TaskStatus(str, Enum):
    pending = "pending"  # Task created but not started
    in_progress = "in_progress"  # User is currently working on it
    blocked = "blocked"  # Waiting on someone/something else
    completed = "completed"  # Task finished successfully
    cancelled = "cancelled"  # Task no longer needs to be done


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, index=True, primary_key=True)
    title: str = Field(nullable=False)
    description: str = Field()
    status: TaskStatus = Field(
        default=TaskStatus.pending,
        sa_column=sq.Column(
            sq.Enum(TaskStatus), nullable=False, server_default=TaskStatus.pending
        ),
    )
    priority: TaskPriority = Field(default=TaskPriority.medium)
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
