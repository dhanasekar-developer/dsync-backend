from email import message
from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.modules.messages.service import MessagesService
from app.modules.chats.service import ChatsService
from app.modules.messages.schemas import CreateMessage, MessageResponse
from app.modules.chats.models import Chat, ChatParticipant
from app.modules.messages.models import Message
from app.modules.users.service import UsersService
from .manager import manager
from app.core.logging import logger

messages_service = MessagesService()

chats_service = ChatsService()

users_service = UsersService()

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

    async def sync_delivered_message(self, user_id: UUID, db: Session):

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

    async def send_initial_presence(self, user_id: UUID, db: Session):
        try:
            related_users = chats_service.get_related_users_with_last_seen(user_id, db)

            users = [ { **user, 'is_online': manager.is_online(str(user['user_id'])) } for user in related_users ]

            await manager.send_to_user(
                str(user_id),
                {
                    'type': 'presence_sync',
                    'users': users
                }
            )
        except Exception as e:
            logger.error('send_initial_presence error ------------- :', str(e))

    async def notify_online(self, user_id: UUID, db: Session):

        related_users = chats_service.get_related_users(user_id, db)

        payload = {
            'type': 'presence_update',
            'data': {
                'user_id': str(user_id),
                'is_online': True,
                'last_seen': None
            }
        }

        for participant_id in related_users:

            await manager.send_to_user(str(participant_id), payload)

    async def notify_offline(self, user_id: UUID, db: Session):
        
        related_users = chats_service.get_related_users(user_id, db)

        last_seen_time = users_service.update_last_seen(user_id, db)

        payload = {
            'type': 'presence_update',
            'data': {
                'user_id': str(user_id),
                'is_online': False,
                'last_seen': last_seen_time
            }
        }

        for participant_id in related_users:

            await manager.send_to_user(str(participant_id), payload)
