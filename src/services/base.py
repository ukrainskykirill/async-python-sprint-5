import logging.config
import uuid
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Generic, Type, TypeVar
from zipfile import ZipFile

import aiofiles
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings
from core.logging import LOGGING
from db.db import Base
from db.redisdb import connection
from models.model import User

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('api_logger')


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class Repository(ABC):

    @abstractmethod
    def get_by_uuid(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_by_path(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_list(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def get_by_uuid(self, db: AsyncSession, user: User, path: str) -> str:
        cache = await connection.get(str(path))
        if cache is not None:
            return cache
        statement = select(self._model).where(self._model.id == path)
        obj = await db.scalar(statement=statement)
        return obj

    async def get_by_path(self, db: AsyncSession, user: User, path: str) -> str:
        statement = select(self._model).where(self._model.path == path)
        obj = await db.scalar(statement=statement)
        return obj

    async def get_list(self, db: AsyncSession, user: User) -> list[ModelType]:
        obj_list = []
        statement = select(self._model).where(self._model.owner == user.id)
        result = await db.execute(statement=statement)
        response = result.fetchall()
        for i in response:
            obj_list.append(i[0])
        return obj_list

    async def zip_create(self, user: User, path: str):
        files = []
        io = BytesIO()
        path = f'{user.id}/{path}'
        for file in Path(path).iterdir():
            files.append(f'{file}')
        with ZipFile(Path(path, app_settings.zip), "w") as zip:
            for file in files:
                zip.write(file)
        return StreamingResponse(
            iter([io.getvalue()]),
            media_type='application/x-zip-compressed'
        )

    async def save_file(self, user: User,  path: str, content: bytes, name: str) -> None:
        folder = f'{user.id}/{path}'
        path = Path(folder)
        if not Path.exists(path):
            Path(path).mkdir(parents=True, exist_ok=True)
        try:
            async with aiofiles.open(Path(path, name), 'wb') as buffer:
                await buffer.write(content)
        except Exception as e:
            logging.warning(f'file has not been saved. Exeption - {e}')

    async def save_redis(self, file_id: uuid.UUID, path: str, name: str) -> None:
        full_path = path+'/'+name
        try:
            await connection.set(str(file_id), full_path, ex=3600)
        except Exception as e:
            logging.warning(f'file has not been added to cache. Exeption - {e}')

    async def create(self, db: AsyncSession, user: User, *, file: UploadFile = File(), path: str) -> ModelType:
        content = file.file.read()
        size = len(content)
        name = file.filename
        db_obj = self._model(
            name=name,
            path=path,
            size=size,
            owner=user.id
        )
        await self.save_file(user=user, path=path, content=content, name=name)
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
        except Exception as e:
            logging.warning(f'file has not been added to db. Exeption - {e}')
            return e
        await self.save_redis(file_id=db_obj.id, path=path, name=name)
        return db_obj
