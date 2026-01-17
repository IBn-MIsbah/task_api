from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import create_task as ct

router = APIRouter()


@router.get("/active", status_code=200, response_model=dict)
async def check_route_status():
    return {"message": "Tasks endpoint is active"}


@router.get("/", status_code=200, response_model=list[TaskRead])
async def read_tasks(
    session: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
):
    statement = select(Task).where(Task.user_id == current_user.id)
    result = await session.execute(statement=statement)
    tasks = result.scalars().all()

    return tasks


@router.post("/", status_code=201)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        new_task = await ct(session=session, task_data=task_data, user=current_user)
        return new_task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}",
        )


@router.patch("/{task_id}", status_code=200, response_model=dict)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this record",
            )
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {"message": "Task updated sussfully!"}
    except Exception:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task: {str(e)}",
        )


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    curretn_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    try:
        task = await session.get(Task, task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        if task.user_id != curretn_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this record",
            )
        await session.delete(task)
        await session.commit()

        return None
    except Exception:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}",
        )
