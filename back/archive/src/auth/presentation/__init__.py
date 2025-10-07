from fastapi import APIRouter

from .routes import auth, user

router = APIRouter()
router.include_router(auth.router, prefix="", tags=["auth"])
router.include_router(user.router, prefix="/users", tags=["users"])