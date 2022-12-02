import uuid
from zipfile import ZipFile
from abc import ABC, abstractmethod
from pathlib import Path
from io import BytesIO
import aiofiles
from fastapi.responses import StreamingResponse
from fastapi import UploadFile, File
from typing import Generic, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from sqlalchemy import select
from src.db.db import Base
from src.models.model import User
from src.db.redisdb import connection

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
    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def get_by_uuid(self, db: AsyncSession, user: User, path: str) -> str:
        key = await connection.get(str(path))
        if key is not None:
            return key
        statement = select(self._model).where(self._model.id == path)
        obj = await db.scalar(statement=statement)
        result = f'{user.id}/{obj.path}/{obj.name}'
        return result

    async def get_by_path(self, db: AsyncSession, user: User, path: str) -> str:
        statement = select(self._model).where(self._model.path == path)
        obj = await db.scalar(statement=statement)
        result = f'{user.id}/{obj.path}/{obj.name}'
        return result

    async def get_multi(self, db: AsyncSession, user: User) -> ModelType:
        statement = select(self._model).where(self._model.owner == user.id)
        result = await db.execute(statement=statement)
        response = result.fetchall()
        return response

    async def zip_create(self, user: User, path: str):
        files = []
        io = BytesIO()
        path = f'{user.id}/{path}'
        for file in Path(path).iterdir():
            files.append(f'{file}')
        with ZipFile('archive.zip', "w") as zip:
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
        async with aiofiles.open(Path(path, name), 'wb') as buffer:
            await buffer.write(content)

    async def save_redis(self, file_id: uuid.UUID, path: str, name: str) -> None:
        full_path = path+'/'+name
        await connection.set(str(file_id), full_path, ex=3600)

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
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        await self.save_redis(file_id=db_obj.id, path=path, name=name)
        return db_obj
