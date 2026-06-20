from urllib import response
from uuid import UUID, uuid4
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from supabase import create_client
from app.core.config import settings
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings

pwd_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def decode_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token Expired!'
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token!'
        )
    
supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

class StorageService:

    @staticmethod
    async def upload_image(id: str | UUID, file: UploadFile, folder: str) -> str:

        extension = file.filename.split('.')[-1]

        if extension not in ('png', 'jpeg', 'jpg'):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Invalid format!"
            )

        file_path = f"{folder}/{id}/{uuid4()}.{extension}"

        try:
            content = await file.read()
        except:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Invalid format!"
            )

        supabase.storage.from_(
            settings.STORAGE_BUCKET_NAME
        ).upload(
            path=file_path,
            file=content,
            file_options={
                'content-type': file.content_type
            }
        )

        return file_path
    
    @staticmethod
    def generate_signed_url(path: str) -> str:
        try:
            path = path.strip()

            if not path:
                return None

            response = (
                supabase.storage
                .from_(settings.STORAGE_BUCKET_NAME)
                .create_signed_url(path=path, expires_in=3600)
            )

            return response['signedURL']
        
        except:
            return None
    
    @staticmethod
    def delete_file(path: str):
        try:
            supabase.storage.from_(settings.STORAGE_BUCKET_NAME).remove(path)

        except:
            pass
