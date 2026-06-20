from fastapi import APIRouter, Depends, Request, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import db_dependency
from app.core.dependencies import CurrentUser
from app.modules.users.schemas import UserResponse
from .schemas import CreateUser, RefreshTokenResponse
from .service import AuthService, UserService


router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

user_service = UserService()
auth_service = AuthService()

@router.post('/signup', response_model=UserResponse, status_code=201)
def create_user(request: CreateUser, db: db_dependency):
    return user_service.create_user(request, db)

@router.post('/login', status_code=status.HTTP_202_ACCEPTED)
def login(response: Response, db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    token_data = auth_service.login(form_data.username, form_data.password, db)

    response.set_cookie(
        key='refresh_token',
        value=token_data['refresh_token'],
        httponly=True,
        secure=False,
        samesite='lax'
    )
    
    return token_data

@router.post('/logout', status_code=status.HTTP_202_ACCEPTED)
def logout(request: Request, response: Response, db: db_dependency):
    refresh_token = request.cookies.get('refresh_token', None)
    logout_message = auth_service.logout(refresh_token, db)
    response.delete_cookie(key='refresh_token')
    return logout_message
    
@router.post('/refresh', response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
def refresh_token(request: Request, db: db_dependency):
    refresh_token = request.cookies.get('refresh_token', None)
    return auth_service.refresh_access_token(refresh_token, db)

@router.get('/current_user', response_model=UserResponse)
def current_user(current_user: CurrentUser):
    return current_user

