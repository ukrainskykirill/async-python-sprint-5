from models.model import FileStorage
from schemas.schemas import FileStorageCreate
from .base import RepositoryDB


class RepositoryShortUrl(RepositoryDB[FileStorage, FileStorageCreate]):
    pass


file_crud = RepositoryShortUrl(FileStorage)


