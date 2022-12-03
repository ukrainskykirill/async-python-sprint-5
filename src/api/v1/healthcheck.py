import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.base import logger
from db.db import get_session
from db.redisdb import connection


router = APIRouter()

@router.get('/ping')
async def ping(
        *,
        db: AsyncSession = Depends(get_session)
) -> any:
    try:
        start_time = time.time()
        await connection.ping()
        finish_time = time.time() - start_time
        redis_ping = {f'{finish_time}'}
    except Exception:
        logger.warning('Redis coonection has no access')
        redis_ping = 'No access'
    try:
        start = time.time()
        conn = await db.connection()
        db_ping = time.time() - start
        if conn:
            logger.info('DB connection access established')
            return {
                'DB connection': f'{db_ping}',
                'Redis': f'{redis_ping}'
            }
    except Exception:
        db_ping = 'No access'
        logger.warning(f'DB connection-{db_ping}, Redis - {redis_ping}')
        return {
            'DB connection': f'{db_ping}',
            'Redis': f'{redis_ping}'
        }
