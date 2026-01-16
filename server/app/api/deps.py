from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    session: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=403, detail="Could not validate credentials"
            )

    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate creadentials")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
