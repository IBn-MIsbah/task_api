from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(session: AsyncSession, task_data: TaskCreate, user: User) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        user_id=user.id,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
