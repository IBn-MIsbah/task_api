from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
