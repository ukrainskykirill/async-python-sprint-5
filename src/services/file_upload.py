from src.models.model import FileStorage
from src.schemas.model import FileStorageCreate
from .base import RepositoryDB


class RepositoryShortUrl(RepositoryDB[FileStorage, FileStorageCreate]):
    pass


file_crud = RepositoryShortUrl(FileStorage)


