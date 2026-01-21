from fastapi import (APIRouter, Body, Depends, HTTPException, Request,
                     Response, status)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import decode_refresh_token, get_current_user
from app.core.db import get_db
from app.core.security import create_access_token as cat
from app.core.security import create_refresh_token as crt
from app.core.security import set_auth_cookeis, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.user_service import create_user

router = APIRouter()


@router.post("/", status_code=201, response_model=UserRead)
async def regist(user_data: UserCreate, session: AsyncSession = Depends(get_db)):
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    try:
        new_user = await create_user(user_in=user_data, session=session)
        return new_user
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@router.post("/login", status_code=200)
async def login(
    response: Response,
    session: AsyncSession = Depends(get_db),
    login_data: UserLogin = Body(...),
):
    statement = select(User).where(User.email == login_data.email)
    user = (await session.execute(statement=statement)).scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        print("password is incorrect")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorect emaill or password",
        )

    access_token = cat(user.id)
    refresh_token = crt(user.id)

    set_auth_cookeis(
        access_token=access_token, refresh_token=refresh_token, response=response
    )

    return {"message": "Logged in seccessfully"}


@router.get("/me", status_code=200, response_model=UserRead)
async def read_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/refresh-token", status_code=200, response_model=dict)
async def refresh_token(
    request: Request, response: Response, session: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token found. Please login.",
        )
    user_id = await decode_refresh_token(refresh_token=refresh_token)

    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive")

    new_access_token = cat(user.id)
    new_refresh_token = crt(user.id)

    set_auth_cookeis(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        response=response,
    )
    return {"message": "Token refreshed successfully!"}


@router.post("/logout", status_code=200)
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}
