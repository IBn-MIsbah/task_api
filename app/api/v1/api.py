from fastapi import APIRouter

from app.api.v1 import users

api_router = APIRouter(redirect_slashes=False, prefix="/api/v1")

api_router.include_router(users.router, prefix="/users", tags=["users"])
