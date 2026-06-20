from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.modules.messages.models import MessageType


class CreateMessage(BaseModel):
    temp_id: UUID
    chat_id: UUID
    message_type: MessageType = MessageType.TEXT
    message_text: str | None = None
    file_url: str | None = None
    reply_to_id: UUID | None = None
    sender_id: UUID = Field(alias='user_id')

class MessageResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    type: str | None = 'new_message'
    temp_id: UUID | None = None
    chat_id: UUID
    id: UUID
    message_type: MessageType = MessageType.TEXT
    message_text: str | None = None
    file_url: str | None = None
    reply_to_id: UUID | None = None
    sender_id: UUID
    created_at: datetime
