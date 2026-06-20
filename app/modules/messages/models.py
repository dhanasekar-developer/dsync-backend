from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, Boolean, Enum as SqlEnum, DateTime, ForeignKey, String
from app.db.base import Base
import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.users.models import UserProfile
    from app.modules.chats.models import Chat

class MessageType(str, Enum):
    TEXT = 'text'
    IMAGE = 'image'
    FILE = 'file'
    AUDIO = 'audio'

class Message(Base):

    __tablename__ = 'messages'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    message_type: Mapped[MessageType] = mapped_column(SqlEnum(MessageType, name='message_type'), nullable=False, default=MessageType.TEXT)
    message_text: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_url: Mapped[str | None] = mapped_column(String, nullable=True)
    reply_to_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('messages.id', ondelete='CASCADE'), nullable=True, index=True)
    reply_to: Mapped['Message | None'] = relationship('Message', remote_side=[id], back_populates='replies')
    replies: Mapped[list['Message']] = relationship('Message', back_populates='reply_to')
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    edited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'), index=True)
    chat: Mapped['Chat'] = relationship(back_populates='messages', foreign_keys=[chat_id])
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('user_profiles.user_id', ondelete='CASCADE'), index=True)
    sender: Mapped['UserProfile'] = relationship(back_populates='messages')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

