from fastapi import APIRouter

from app.api.v1 import tasks, users, auth

api_router = APIRouter(redirect_slashes=False, prefix="/api/v1")

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])