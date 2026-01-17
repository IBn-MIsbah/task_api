from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.db import get_db
from app.models.user import Role, User
from app.schemas.user import UserRead, UserUpdate
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


@router.patch("/{user_id}", status_code=204)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to update this record",
        )
    try:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account has been blocked!",
            )

        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return None
    except Exception:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user data: {str(e)}",
        )

@router.delete('/{user_id}', status_code=200)
async def delete_user(user_id:UUID, session:AsyncSession=Depends(get_db), current_user:User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
            ,detail="Unauthorized to remove this record"
        )
    try:
        user = await session.get(User, user_id)
        await session.delete(user)
        await session.commit()
        return None
    except Exception:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user data: {str(e)}"
        )