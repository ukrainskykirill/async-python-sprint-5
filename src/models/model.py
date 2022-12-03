import uuid
from datetime import datetime

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import Base, get_session


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = 'user'
    username = Column(String(50))


class FileStorage(Base):
    __tablename__ = 'filestorage'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100))
    path = Column(Text)
    size = Column(Integer)
    is_downloadable = Column(Boolean, default=True)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    owner = Column(ForeignKey('user.id'))


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)
