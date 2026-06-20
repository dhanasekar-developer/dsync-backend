from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, UUID, DateTime, Integer, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.users.models import UserProfile


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('user_profiles.user_id', ondelete='CASCADE'), index=True)
    user: Mapped['UserProfile'] = relationship(back_populates='refresh_tokens')
    token: Mapped[str] = mapped_column(String(500), index=True, unique=True)
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)