from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

load_dotenv()


class AppSettings(BaseSettings):
    app_title: str
    database_dsn: PostgresDsn
    host: str
    port: int
    secret: str
    redis_port: int
    redis_host: str
    zip: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_settings = AppSettings()
