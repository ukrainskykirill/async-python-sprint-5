import uuid
from datetime import datetime

from pydantic import BaseModel


#мы же все равно используем эти схемы для создания, обновления, возврата клиенту и тд, каждая отвечает за свое
#было бы не правильно все возложить только на базовую?


class FileStorageBase(BaseModel):
    path: str


class FileStorageCreate(FileStorageBase):
    pass


class FileStorageInDBBase(FileStorageBase):
    id: uuid.UUID
    name: str
    path: str
    size: int
    is_downloadable: bool
    created_at: datetime

    class Config:
        orm_mode = True


class FileStorage(FileStorageInDBBase):
    pass


class FileStorageInDB(FileStorageInDBBase):
    pass


class GetList(BaseModel):
    __root__: list[FileStorage]
