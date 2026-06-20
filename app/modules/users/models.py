from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, String, UUID, DateTime, UniqueConstraint
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.auth.models import RefreshToken
    from app.modules.chats.models import Chat, ChatParticipant
    from app.modules.messages.models import Message

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(250), unique=True, index=True)
    image: Mapped[str | None] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    refresh_tokens: Mapped[list['RefreshToken']] = relationship(back_populates='user', cascade='all, delete-orphan')
    chats: Mapped[list['Chat']] = relationship(back_populates='created_by')
    chat_participants: Mapped[list['ChatParticipant']] = relationship(back_populates='user', cascade='all, delete-orphan')
    messages: Mapped[list['Message']] = relationship(back_populates='sender', cascade='all, delete-orphan')

    __table_args__ = (
        UniqueConstraint( "email", name='uq_user_email' ),
    )
