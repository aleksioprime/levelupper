from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from src.db.postgres import get_db_session
from src.db.redis import get_redis

router = APIRouter()