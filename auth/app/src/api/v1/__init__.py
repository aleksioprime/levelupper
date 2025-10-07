from fastapi import APIRouter
from .ping import ping
from .users import auth, user

router = APIRouter()
router.include_router(ping.router, prefix="", tags=["ping"])
router.include_router(auth.router, prefix="", tags=["auth"])
router.include_router(user.router, prefix="/users", tags=["users"])