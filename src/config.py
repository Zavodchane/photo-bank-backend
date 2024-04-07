import os
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SERVICE_NAME = os.getenv("SERVICE_NAME")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")


class App(BaseModel):
    title: str = "Photo Bank"
    prefix: str = "/api/v1"


class DataBase(BaseModel):
    url: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    echo: bool = True


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"

    access_token_expire_minutes: int = 10000
    refresh_token_expire_minutes: int = 30


class Redis(BaseModel):
    host: str = REDIS_HOST
    port: int = REDIS_PORT

    refresh_token_expire_seconds: int = AuthJWT().refresh_token_expire_minutes * 60


class S3Storage(BaseModel):
    config: dict = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "service_name": SERVICE_NAME,
        "endpoint_url": ENDPOINT_URL,
    }

    photo_bucket: str = "russpass-photo-bank"

    expires_photo_url: int = 60 * 60 * 24 * 365


class Celery(BaseModel):
    broker: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    backend: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"


class AIModelsApi(BaseModel):
    url_all: str = "http://127.0.0.1:8001/api/v1/model/all"


class Settings(BaseSettings):

    app: App = App()

    database: DataBase = DataBase()

    auth_jwt: AuthJWT = AuthJWT()

    redis: Redis = Redis()

    s3_storage: S3Storage = S3Storage()

    celery: Celery = Celery()

    ai_api: AIModelsApi = AIModelsApi()


settings = Settings()
