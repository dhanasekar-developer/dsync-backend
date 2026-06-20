from email import message
from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.modules.messages.service import MessagesService
from app.modules.chats.service import ChatsService
from app.modules.messages.schemas import CreateMessage, MessageResponse
from app.modules.chats.schemas import ChatParticipantResponse
from app.modules.chats.models import Chat, ChatParticipant
from app.modules.messages.models import Message
from .manager import manager


messages_service = MessagesService()

chats_service = ChatsService()

class SocketChatService:

    async def send_message(self, payload: CreateMessage, db: Session):

        message_res = messages_service.create_message(payload, db)

        message = MessageResponse.model_validate(message_res).model_dump(mode='json')

        participant_ids = chats_service.get_chat_participant_ids(payload.chat_id, db)

        for id in participant_ids:
            await manager.send_to_user(str(id), message)

    async def handle_received_message(self, payload, db: Session):

        payload_type = payload.get('type', None)

        if payload_type == 'new_message':
            payload = CreateMessage.model_validate(payload)
            await self.send_message(payload, db)

        elif payload_type == 'message_delivered' or payload_type == 'message_read':

            if payload_type == 'message_delivered':
                participant = chats_service.update_last_delivered_message(payload['chat_id'], payload['message_id'], payload['user_id'], db)
            elif payload_type == 'message_read':
                participant = chats_service.update_last_read_message(payload['chat_id'], payload['message_id'], payload['user_id'], db)

            payload = {
                'type': payload_type,
                'chat_id': payload['chat_id'],
                'last_delivered_message_id': payload['message_id'],
                'last_delivered_at': participant.last_delivered_at.isoformat() if participant.last_delivered_at else None,
                'delivered_user_id': str(payload['user_id']),
                'last_read_message_id': payload['message_id'],
                'last_read_at': participant.last_read_at.isoformat() if participant.last_read_at else None,
                'read_user_id': str(payload['user_id']),
            }

            await manager.send_to_user(str(participant.last_delivered_message.sender_id), payload)

    async def sync_delivered_message(self, user_id, db: Session):
        user_id = UUID(user_id)

        chats = db.execute(
            select(Chat)
            .where(Chat.chat_participants.any(ChatParticipant.user_id == user_id))
            .options(selectinload(Chat.chat_participants))
        ).scalars().all()

        for chat in chats:

            last_message = db.execute(
                select(Message)
                .where(Message.chat_id == chat.id, Message.sender_id != user_id)
                .order_by(Message.created_at.desc())
            ).scalars().first()

            if last_message:
                
                payload = {
                    'type': 'message_delivered',
                    'chat_id': str(chat.id),
                    'message_id': str(last_message.id),
                    'user_id': user_id
                }

                await self.handle_received_message(payload, db)

            