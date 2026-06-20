from typing import Annotated
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.common.utils import StorageService, decode_token
from sqlalchemy import select
from app.db.database import db_dependency
from app.modules.users.models import UserProfile
from app.modules.auth.schemas import TokenData

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

storage_service = StorageService()

def get_current_user(db: db_dependency, token: str = Depends(oauth_scheme)):

    payload = decode_token(token)

    if payload.get('type', None) != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid access token!'
        )
    
    stmt = select(UserProfile).where(UserProfile.user_id == payload['sub'])
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found!'
        )
    
    if user.image:
        user.image = storage_service.generate_signed_url(user.image)
    
    return user

def get_current_token(db: db_dependency, token: str = Depends(oauth_scheme)):
    payload = decode_token(token)

    if payload.get('type', None) != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid access token!'
        )
    
    
    
    return { **payload, 'user_id': UUID(payload['sub']) }
    

CurrentUser = Annotated[UserProfile, Depends(get_current_user)]

CurrentToken = Annotated[TokenData, Depends(get_current_token)]