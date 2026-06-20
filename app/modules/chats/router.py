from uuid import UUID
from fastapi import APIRouter, status
from app.db.database import db_dependency
from app.modules.chats.service import ChatsService
from app.modules.chats.schemas import CreateChat, ChatResponse, ChatParticipantResponse
from app.core.dependencies import CurrentToken

router = APIRouter(
    prefix='/chats',
    tags=['Chats']
)

chats_service = ChatsService()

@router.get('/chat_list', response_model=list[ChatResponse], status_code=status.HTTP_200_OK)
def chat_list(db: db_dependency, current_token: CurrentToken):
    return chats_service.get_chat_list(current_token['user_id'], db)

@router.post('/create_chat', response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(request: CreateChat, db: db_dependency, current_token: CurrentToken):
    print('request:--------------------------',request)
    return chats_service.create_chat(current_token['user_id'], request, db)

@router.get('/chat_participants_list', response_model=list[ChatParticipantResponse], status_code=status.HTTP_200_OK)
def chat_participants_list(chat_id, db: db_dependency, current_token: CurrentToken):
    return chats_service.get_chat_participants(chat_id, db)