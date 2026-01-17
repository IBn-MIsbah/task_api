from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.db import get_db
from app.models.user import Role, User
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import create_user as cr

router = APIRouter()


@router.get("/active", status_code=200, response_model=dict)
async def check_route_status():
    return {"message": "Users endpoint is active"}


@router.get("/", status_code=200, response_model=list[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_db),
    user_rol: Role = Depends(require_role(Role.admin)),
):
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


@router.get("/{user_id}", status_code=200, response_model=UserRead)
async def get_user(user_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement=statement)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user
    except HTTPException:
        raise
    except Exception as e:

        await session.rollback()  # rollback is usually only needed for POST/PUT/DELETE
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred. {str(e)}",
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
