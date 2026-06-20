from fastapi import APIRouter, status
from app.db.database import db_dependency
from app.modules.messages.service import MessagesService

router = APIRouter(
    prefix='/messages',
    tags=['Message']
)

messages_service = MessagesService()

@router.get('/chat_messages', status_code=status.HTTP_200_OK)
def get_messages(chat_id, db: db_dependency):
    return messages_service.get_messages(chat_id, db)
