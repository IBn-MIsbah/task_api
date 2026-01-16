from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import create_access_token as cat
from app.models.user import User

router = APIRouter()


@router.post("/login", status_code=200)
async def login_access_token(
    session: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    statement = select(User).where(User.email == form_data.username)
    user = (await session.execute(statement=statement)).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorect emaill or password"
        )

    return {"access_token": cat(user.id), "token_type": "bearer"}
