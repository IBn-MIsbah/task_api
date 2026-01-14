from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import create_user as cr

router = APIRouter()


@router.get("/active", status_code=200, response_model=dict)
async def check_route_status():
    return {"message": "Users endpoint is active"}


@router.get("/", status_code=200, response_model=list[UserRead])
async def read_users(session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(select(User))
        users = result.scalars().all()

        return users
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}",
        )


@router.post("/", status_code=201, response_model=UserRead)
async def create_user(user_data: UserCreate, session: AsyncSession = Depends(get_db)):
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    try:
        new_user = await cr(user_in=user_data, session=session)
        return new_user
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )
