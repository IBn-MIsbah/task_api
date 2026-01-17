from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.models.user import Role, User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
    # token: str = Depends(reusable_oauth2),
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    try:
        payload = jwt.decode(
            token, settings.ACCESS_TOKEN_SECRET_KEY, algorithms=settings.ALGORITHM
        )
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


def require_role(*roles: Role):
    def role_dependecy(current_user: User = Depends(get_current_user)):
        print(f"Current user role: {current_user.role}")
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user

    return role_dependecy


async def decode_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.REFRESH_TOKEN_SECRET_KEY,
            algorithms=settings.ALGORITHM,
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cound not validate credential",
            )
        return user_id
    except JWTError:
        raise HTTPException(status_code=404, detail="User not found")
