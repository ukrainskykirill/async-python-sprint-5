import uuid
from datetime import datetime
from pydantic import BaseModel

#это разве не стандартный набор схем на создание, обновление, возврат клиенту
#пускай они сейчас и не расширяют функционал, но могут пригодиться


class FileStorageBase(BaseModel):
    path: str


class FileStorageCreate(FileStorageBase):
    pass


class FileStorageUpdate(FileStorageBase):
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
