from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.messages.models import Message
from app.modules.messages.schemas import CreateMessage
from app.modules.chats.service import ChatsService

chats_service = ChatsService()


class MessagesService:
    def get_messages(self, chat_id: UUID, db: Session):
        messages = db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
        ).scalars().all()
        
        return messages

    def create_message(self, payload: CreateMessage, db: Session):
        message = Message(**payload.model_dump(exclude={'temp_id'}))

        db.add(message)
        db.commit()
        db.refresh(message)

        chats_service.update_chat_last_message(message.chat_id, message.id, message.created_at, db)

        message.temp_id = payload.temp_id

        return message