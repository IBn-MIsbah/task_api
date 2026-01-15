from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.task import Task
from app.schemas.task import TaskRead
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/active", status_code=200, response_model=dict)
async def check_route_status():
    return {"message": "Tasks endpoint is active"}


@router.get('/', status_code=200, response_model=list[TaskRead] )
async def read_tasks( session: AsyncSession = Depends(get_db),current_user:UUID = Depends(get_current_user)):
    statement = select(Task).where(Task.user_id == current_user.id)
    result = await session.execute(statement=statement)
    tasks = result.scalars().all()

    return tasks
