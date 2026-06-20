from datetime import datetime, timezone, timedelta
from uuid import UUID
from .models import RefreshToken
from app.modules.users.models import UserProfile
from .schemas import CreateUser
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from fastapi import HTTPException, status
from app.common.utils import hash_password, verify_password, decode_token
from jose import jwt
from app.core.config import settings
import hashlib


class UserService:
    def create_user(self, payload: CreateUser, db: Session):
        existing_user = db.query(UserProfile).filter(UserProfile.email == payload.email).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email already exist, So try with another email!'
            )
        
        user = UserProfile(**payload.model_dump(exclude={'password'}), password = hash_password(payload.password))
        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    
class AuthService:
    def login(self, email: str, password: str, db: Session):
        existing_user = db.execute(select(UserProfile).where(UserProfile.email == email)).scalar_one_or_none()

        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not exist!'
            )
        
        if not verify_password(password, existing_user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Incorrect password!'
            )
        
        access_token = self.__create_access_token(existing_user.user_id, existing_user.email)

        refresh_token = self.__create_refresh_token(existing_user.user_id, db)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        }
    
    def logout(self, refresh_token: str, db: Session):

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Token Required!'
            )
        
        hashed_token = self.__hash_token(refresh_token)

        token_record = db.scalar(select(RefreshToken).where(RefreshToken.token == hashed_token))

        if token_record:
            token_record.revoked = True
            db.commit()

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid Token!'
            ) 

        return {
            'message': 'User logout successfully'
        }
    
    def refresh_access_token(self, refresh_token: str, db: Session):

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Token Required!'
            )

        token_data = decode_token(refresh_token)

        if token_data['type'] != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid Token!'
            )

        # token_record = db.query(RefreshToken).options(joinedload(RefreshToken.user)).filter(RefreshToken.token == refresh_token).first()

        hashed_token = self.__hash_token(refresh_token)

        stmt = select(RefreshToken).options(joinedload(RefreshToken.user)).where(RefreshToken.token == hashed_token)

        token_record = db.execute(stmt).scalar_one_or_none()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid Token!!!'
            )
        
        if token_record.revoked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Token Expired!'
            )
        
        access_token = self.__create_access_token(token_record.user.user_id, token_record.user.email)

        return {
            'access_token': access_token,
            'token_type': 'bearer'
        }
        
    def __create_access_token(self, user_id: UUID, email: str):

        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            'sub': str(user_id),
            'email': email,
            'type': 'access',
            'exp': expire,
        }

        return jwt.encode(payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def __create_refresh_token(self, user_id: UUID, db: Session):
        
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            'sub': str(user_id),
            'type': 'refresh',
            'exp': expire
        }

        refresh_token = jwt.encode(payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        hashed_token = self.__hash_token(refresh_token)
    
        refresh_record = RefreshToken(
            user_id = user_id,
            token = hashed_token,
            expire_at = expire
        )

        db.add(refresh_record)
        db.commit()

        return refresh_token
    
    def __hash_token(self, token: str):
        return hashlib.sha256(token.encode()).hexdigest()
    
