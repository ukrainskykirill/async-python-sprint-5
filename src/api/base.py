import logging.config
from uuid import UUID
import time
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import src.schemas.model as schema
from src.db.db import get_session
from src.core.logging import LOGGING
from src.models.model import User
from src.services.file_upload import file_crud
from fastapi.responses import FileResponse
from src.users.manager import current_user
from src.db.redisdb import connection

router = APIRouter()

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('api_logger')


@router.get('/ping')
async def ping(
        *,
        db: AsyncSession = Depends(get_session)
) -> any:
    try:
        start1 = time.time()
        await connection.ping()
        finish2 = time.time() - start1
        start = time.time()
        conn = await db.connection()
        finish = time.time() - start
        if conn:
            logger.info('DB connection access established')
            return {
                'DB connection ping': f'{finish}',
                'Redis ping': f'{finish2}'
            }
    except Exception:
        logger.warning('DB coonection has no access')
        return {'DB connection or Redis': 'No access'}


@router.get('/files/list', response_model=schema.Multi)
async def list_files(
        *,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_user)
) -> any:
    response = await file_crud.get_multi(db=db, user=user)
    logger.info('Created list of files for user')
    return {'owner': str(user.id), "files": response}


@router.get('/files/download')
async def files_download(
        *,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_user),
        path: str,
        compression_type: str = None
) -> any:
    if compression_type:
        file = await file_crud.zip_create(path=path, user=user)
        logger.info('Downloading zip')
        return file
    try:
        if UUID(path):
            logger.info('Downloading file by uuid')
            path = await file_crud.get_by_uuid(db=db, path=path, user=user)
            return FileResponse(path=path, media_type="application/octet-stream")
    except Exception:
        path = await file_crud.get_by_path(db=db, user=user, path=path)
        logger.info('Downloading file by path')
        return FileResponse(path=path, media_type="application/octet-stream")


@router.post('/files/upload', response_model=schema.FileStorage, status_code=status.HTTP_201_CREATED)
async def files_upload(
        *,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_user),
        file: UploadFile = File(),
        path: str
) -> any:
    file_obj = await file_crud.create(db=db, user=user, file=file, path=path)
    logger.info('Uploading file')
    return file_obj
