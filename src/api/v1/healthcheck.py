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
        start = time.time()
    except Exception:
        logger.warning('Redis coonection has no access')
        return {'Redis': 'No access'}
    try:
        conn = await db.connection()
        finish = time.time() - start
        if conn:
            logger.info('DB connection access established')
            return {
                'DB connection ping': f'{finish}',
                'Redis ping': f'{finish_time}'
            }
    except Exception:
        logger.warning('DB coonection has no access')
        return {'DB connection or Redis': 'No access'}
