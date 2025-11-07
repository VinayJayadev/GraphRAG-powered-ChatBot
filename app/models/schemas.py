from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Message Schemas
class MessageBase(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    conversation_id: UUID


class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime

    @classmethod
    def model_validate(cls, obj):
        """Override to map message_data to metadata"""
        if hasattr(obj, 'message_data'):
            # Create a dict with metadata mapped from message_data
            data = {
                'id': obj.id,
                'conversation_id': obj.conversation_id,
                'role': obj.role.value if hasattr(obj.role, 'value') else obj.role,
                'content': obj.content,
                'created_at': obj.created_at,
                'metadata': obj.message_data or {}
            }
            return cls(**data)
        return super().model_validate(obj)

    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationBase(BaseModel):
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(ConversationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []


class ConversationListItem(BaseModel):
    id: UUID
    title: str
    updated_at: datetime
    preview: Optional[str] = None  # Last message preview
    message_count: int = 0

    class Config:
        from_attributes = True


# Chat Request/Response with conversation support
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None
    chat_history: List[Dict[str, str]] = []  # For backward compatibility


class ChatResponse(BaseModel):
    response: str
    conversation_id: UUID
    context: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    sources: Optional[List[Dict[str, Any]]] = None  # Document sources

