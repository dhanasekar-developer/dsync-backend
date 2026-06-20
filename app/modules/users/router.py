from fastapi import APIRouter, File, Request, UploadFile, status
from app.db.database import db_dependency
from app.modules.users.service import UsersService
from app.modules.users.schemas import PasswordChangeRequest, UserProfileUpdate, UserResponse
from app.core.dependencies import CurrentToken


router = APIRouter(
    prefix='/users',
    tags=['Users']
)

users_service = UsersService()

@router.get('/search', response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def search_users(search: str, db: db_dependency, current_token: CurrentToken):
    return users_service.search_user(search, current_token, db)

@router.put('/update_profile_image', status_code=status.HTTP_201_CREATED)
async def update_profile_image(db: db_dependency, current_token: CurrentToken, image: UploadFile = File(...)):
    user_id = current_token['user_id']
    return await users_service.update_user_profile_image(user_id, image, db)

@router.put('/update_profile', status_code=status.HTTP_200_OK)
def update_profile(request: UserProfileUpdate, db: db_dependency, current_token: CurrentToken):
    user_id = current_token['user_id']
    users_service.update_user_profile(user_id, request, db)
    ...

@router.put('/password_change', status_code=status.HTTP_200_OK)
def password_change(request: PasswordChangeRequest, db: db_dependency, current_token: CurrentToken):
    user_id = current_token['user_id']
    users_service.password_change(user_id, request, db)
    ...