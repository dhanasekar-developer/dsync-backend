from datetime import datetime
from pydantic import BaseModel, Field, computed_field, model_serializer
from uuid import UUID

from app.modules.chats.models import ChatType
from app.modules.users.schemas import UserResponse
from app.modules.messages.schemas import MessageResponse

class CreateChat(BaseModel):
    users_list: list[UUID]
    chat_type: str

class ChatResponse(BaseModel):
    chat_id: UUID
    chat_type: ChatType
    name: str
    image: str | None
    last_message_type: str | None = None
    last_message_text: str | None = None

class ChatParticipantResponse(BaseModel):
    id: UUID
    chat_id: UUID
    user_id: UUID
    user: UserResponse
    last_delivered_message_id: UUID | None = None
    last_delivered_message: MessageResponse | None = None
    last_delivered_at: datetime | None = None
    last_read_message_id: UUID | None = None
    last_read_message: MessageResponse | None = None
    last_read_at: datetime | None = None

    @computed_field
    @property
    def user_name(self) -> str:
        return self.user.name
    
    @computed_field
    @property
    def last_delivered_message_sender_id(self) -> UUID | None:
        return self.last_delivered_message.sender_id if self.last_delivered_message else None
    
    @computed_field
    @property
    def last_read_message_sender_id(self) -> UUID | None:
        return self.last_read_message.sender_id if self.last_read_message else None
    
    @model_serializer(mode='wrap')
    def serializer(self, handler):
        data = handler(self)

        data.pop('user', None)
        data.pop('last_delivered_message', None)
        data.pop('last_read_message', None)

        return data