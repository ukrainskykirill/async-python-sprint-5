import uuid
from datetime import datetime
from pydantic import BaseModel


class FileStorageBase(BaseModel):
    path: str


class FileStorageCreate(FileStorageBase):
    pass


class FileStorageUpdate(FileStorageBase):
    pass


class FileStorageInDBBase(FileStorageBase):
    id: str | uuid.UUID
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


class Multi(BaseModel):
    owner: uuid.UUID
    files: list
