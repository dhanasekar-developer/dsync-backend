from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = 'Chat Application'
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    REDIS_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    ACCESS_KEY_ID: str
    SECRET_ACCESS_KEY: str
    STORAGE_BUCKET_NAME: str
    S3_ENDPOINT_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    PROFILE_IMAGE_FOLDER: str

    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env')

settings = Settings()