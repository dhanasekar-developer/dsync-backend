from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload, joinedload
from app.modules.chats.schemas import CreateChat
from app.common.utils import StorageService
from .models import Chat, ChatParticipant, ChatType
from uuid import UUID

storage_service = StorageService()

class ChatsService:
    def get_chat_list(self, current_user_id: UUID,  db: Session):

        stmt = (
            select(Chat).where(Chat.chat_participants.any(ChatParticipant.user_id == current_user_id))
            .options(
                selectinload(Chat.chat_participants).selectinload(ChatParticipant.user),
                joinedload(Chat.last_message)
            )
            .order_by(Chat.last_message_at.desc())
        )

        chats = db.execute(stmt).scalars().all()

        result = []

        for chat in chats:
            last_message = chat.last_message

            common = {
                'chat_id': chat.id,
                'chat_type': chat.chat_type,
                'last_message_text': last_message.message_text if last_message else None,
                'last_message_type': last_message.message_type if last_message else None,
            }

            if chat.chat_type == ChatType.GROUP:
                result.append({
                    **common,
                    'name': chat.name,
                    'image': storage_service.generate_signed_url(other_user.image),
                })

            else:
                other_user = next( p.user for p in chat.chat_participants if p.user_id != current_user_id )

                result.append({
                    **common,
                    'name': other_user.name,
                    'image': storage_service.generate_signed_url(other_user.image),
                })

        return result


    def create_chat(self, current_user_id: UUID, payload: CreateChat, db: Session):

        if payload.chat_type == ChatType.PRIVATE:

            other_user = payload.users_list[0]

            chat_existing = db.execute(
                select(Chat).where(
                    Chat.chat_type == ChatType.PRIVATE,
                    Chat.chat_participants.any(ChatParticipant.user_id == current_user_id),
                    Chat.chat_participants.any(ChatParticipant.user_id == other_user)
                ).options(
                    selectinload(Chat.chat_participants).selectinload(ChatParticipant.user)
                )
            ).scalar_one_or_none()

            if chat_existing:
                other_user = next(p.user for p in chat_existing.chat_participants if p.user_id != current_user_id)

                return {
                    'chat_id': chat_existing.id,
                    'chat_type': chat_existing.chat_type,
                    'name': other_user.name,
                    'image': storage_service.generate_signed_url(other_user.image),
                }

        chat = Chat(created_by_id=current_user_id, chat_type=payload.chat_type)

        db.add(chat)
        db.flush()

        participant_ids = set(payload.users_list)
        participant_ids.add(current_user_id)

        chat_participants = [ ChatParticipant(chat_id=chat.id, user_id=user_id) for user_id in participant_ids ]

        db.add_all(chat_participants)
        db.commit()

        db.refresh(chat)

        other_user = next(p.user for p in chat.chat_participants if p.user_id != current_user_id)

        return {
            'chat_id': chat.id,
            'chat_type': chat.chat_type,
            'name': other_user.name,
            'image': storage_service.generate_signed_url(other_user.image),
        }
    
    def get_chat_participants(self, chat_id: UUID, db: Session):

        return db.execute(
                select(ChatParticipant)
                .where(ChatParticipant.chat_id == chat_id)
                .options(
                    joinedload(ChatParticipant.user)
                )
                
            ).scalars().all()

    def get_chat_participant_ids(self, chat_id: UUID, db: Session):

        participants = db.execute(
                select(ChatParticipant)
                .where(ChatParticipant.chat_id == chat_id)
                
            ).scalars().all()
        
        return [ participant.user_id for participant in participants  ]
        
    def update_chat_last_message(self, chat_id, message_id, message_at, db: Session):

        db.execute(update(Chat).where(Chat.id == chat_id).values(last_message_id=message_id, last_message_at=message_at))
        db.commit()

    def update_last_delivered_message(self, chat_id, message_id, user_id, db: Session):
        db.execute(
            update(ChatParticipant)
            .where(ChatParticipant.chat_id == chat_id, ChatParticipant.user_id == user_id)
            .values(last_delivered_message_id = message_id, last_delivered_at = datetime.now(timezone.utc))
        )

        db.commit()

        return self.get_chat_participant(chat_id, user_id, db)
    
    def update_last_read_message(self, chat_id, message_id, user_id, db: Session):
        db.execute(
            update(ChatParticipant)
            .where(ChatParticipant.chat_id == chat_id, ChatParticipant.user_id == user_id)
            .values(last_read_message_id = message_id, last_read_at = datetime.now(timezone.utc))
        )

        db.commit()

        return self.get_chat_participant(chat_id, user_id, db)

    def get_chat_participant(self, chat_id, user_id, db: Session):
        return db.execute(
            select(ChatParticipant)
            .where(ChatParticipant.chat_id == chat_id, ChatParticipant.user_id == user_id)
        ).scalar_one()