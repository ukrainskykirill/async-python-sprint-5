import logging.config
from uuid import UUID
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import schemas.schemas as schema
from db.db import get_session
from core.logging import LOGGING
from models.model import User
from services.file_upload import file_crud
from fastapi.responses import FileResponse
from users.manager import current_user

router = APIRouter()

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('api_logger')


@router.get('/files/list', response_model=schema.GetList)
async def list_files(
        *,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_user)
) -> any:
    response = await file_crud.get_list(db=db, user=user)
    logger.info('Created list of files for user')
    return response


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
        #здесь идет проверка, пришел нам uuid или путь, если путь, то мы попадаем в эксепшн и работаем там
        if UUID(path):
            logger.info('Downloading file by uuid')
            obj = await file_crud.get_by_uuid(db=db, path=path, user=user)
            path = f'{user.id}/{obj.path}/{obj.name}'
            return FileResponse(path=path, media_type="application/octet-stream")
    except Exception:
        logger.info('Downloading file by path')
        obj = await file_crud.get_by_path(db=db, user=user, path=path)
        path = f'{user.id}/{obj.path}/{obj.name}'
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
    print(f'type - {type(file_obj)}')
    return file_obj

