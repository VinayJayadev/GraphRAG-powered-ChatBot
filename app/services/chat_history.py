from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.chat_models import Conversation, Message, MessageRole
from app.models.schemas import ConversationCreate, ConversationUpdate, MessageCreate


class ChatHistoryService:
    """Service for managing chat history and conversations"""

    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, title: str, user_id: Optional[str] = None) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            title=title,
            user_id=user_id
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_conversation_with_messages(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get a conversation with all its messages"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def list_conversations(self, user_id: Optional[str] = None, limit: int = 50) -> List[Conversation]:
        """List all conversations, optionally filtered by user_id"""
        query = self.db.query(Conversation)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        return query.order_by(desc(Conversation.updated_at)).limit(limit).all()

    def update_conversation(self, conversation_id: UUID, update_data: ConversationUpdate) -> Optional[Conversation]:
        """Update a conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None

        if update_data.title is not None:
            conversation.title = update_data.title
            conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation and all its messages"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()
        return True

    def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole(role),
            content=content,
            message_data=metadata or {}
        )
        self.db.add(message)

        # Update conversation's updated_at timestamp
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, conversation_id: UUID, limit: Optional[int] = None) -> List[Message]:
        """Get messages for a conversation"""
        query = self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at)
        if limit:
            query = query.limit(limit)
        return query.all()

    def generate_conversation_title(self, first_message: str, max_length: int = 50) -> str:
        """Generate a title from the first message"""
        # Remove extra whitespace and limit length
        title = first_message.strip()
        if len(title) > max_length:
            title = title[:max_length].rsplit(' ', 1)[0] + "..."
        return title or "New Conversation"

