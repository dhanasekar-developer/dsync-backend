from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, Boolean, Enum as SqlEnum, DateTime, ForeignKey, String, UniqueConstraint
from app.db.base import Base
import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.users.models import UserProfile
    from app.modules.messages.models import Message

class ChatType(str, Enum):
    PRIVATE = 'private'
    GROUP = 'group'

class Chat(Base):

    __tablename__ = 'chats'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str | None] = mapped_column(String(100)) 
    image: Mapped[str | None] = mapped_column(String(200)) 
    chat_type: Mapped[ChatType] = mapped_column(SqlEnum(ChatType, name='chat_type'), nullable=False, default=ChatType.PRIVATE)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('user_profiles.user_id', ondelete='CASCADE'), index=True)
    created_by: Mapped['UserProfile'] = relationship(back_populates='chats')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_message_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('messages.id', ondelete='SET NULL'), nullable=True)
    last_message: Mapped['Message | None'] = relationship(foreign_keys=[last_message_id])
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    chat_participants: Mapped[list['ChatParticipant']] = relationship(back_populates='chat', cascade='all, delete-orphan')
    messages: Mapped[list['Message']] = relationship(back_populates='chat', cascade='all, delete-orphan', foreign_keys='Message.chat_id')

class ChatParticipant(Base):

    __tablename__ = 'chat_participants'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('chats.id', ondelete='CASCADE'), index=True)
    chat: Mapped['Chat'] = relationship(back_populates='chat_participants')
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('user_profiles.user_id', ondelete='CASCADE'), index=True)
    user: Mapped['UserProfile'] = relationship(back_populates='chat_participants')
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_delivered_message_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('messages.id', ondelete='SET NULL'), nullable=True, index=True)
    last_delivered_message: Mapped['Message | None'] = relationship(foreign_keys=[last_delivered_message_id])
    last_delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_read_message_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('messages.id', ondelete='SET NULL'), nullable=True, index=True)
    last_read_message: Mapped['Message | None'] = relationship(foreign_keys=[last_read_message_id])
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (UniqueConstraint('chat_id', 'user_id', name='uq_chat_user'), )
