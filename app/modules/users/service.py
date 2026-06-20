from uuid import UUID
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, or_, update
from app.modules.auth.schemas import TokenData
from app.common.utils import StorageService, hash_password, verify_password
from app.modules.users.schemas import PasswordChangeRequest, UserProfileUpdate
from .models import UserProfile
from sqlalchemy.orm import Session
from app.core.config import settings
from sqlalchemy.exc import IntegrityError

storage_service = StorageService()


class UsersService:
    def search_user(self, search: str, token_data: TokenData, db: Session):
        stmt = select(UserProfile).where(
            or_(
                UserProfile.name.ilike(f"%{search}%"),
                UserProfile.email.ilike(f"%{search}%")
            ),
            UserProfile.user_id != token_data['user_id']
        ).limit(50)

        users = db.execute(stmt).scalars().all()

        for user in users:
            user.image = storage_service.generate_signed_url(user.image)

        return users
    
    def update_user_profile(self, user_id: UUID, payload: UserProfileUpdate, db: Session):
        try:
            db.execute(
                update(UserProfile)
                .where(UserProfile.user_id == user_id)
                .values(**payload.model_dump())
            )

            db.commit()

        except IntegrityError as e:
            db.rollback()

            # error = str(e)

            # if 'ix_user_profiles_email' in error:
            #     raise HTTPException(
            #         status_code=status.HTTP_400_BAD_REQUEST,
            #         detail='Email already register with another account!'
            #     )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email already register with another account!'
            )

    async def update_user_profile_image(self, user_id: UUID, image: UploadFile, db: Session):

        user = db.execute(select(UserProfile).where(UserProfile.user_id == user_id)).scalar_one()

        if user.image:
            storage_service.delete_file(user.image)
        
        path = await storage_service.upload_image(user_id, image, settings.PROFILE_IMAGE_FOLDER)

        db.execute(update(UserProfile).where(UserProfile.user_id == user_id).values(image = path))

        db.commit()

        return { 'image': storage_service.generate_signed_url(path) }
    
    def password_change(self, user_id: UUID, payload: PasswordChangeRequest, db: Session):

        user_profile = db.execute(select(UserProfile).where(UserProfile.user_id == user_id)).scalar_one()

        is_password_match = verify_password(payload.current_password, user_profile.password)

        if not is_password_match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect!"
            )
        
        hashed_password = hash_password(payload.new_password)

        db.execute(update(UserProfile).where(UserProfile.user_id == user_id).values(password = hashed_password))

        db.commit()