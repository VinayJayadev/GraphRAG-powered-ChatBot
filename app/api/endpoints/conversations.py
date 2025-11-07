from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import List
from uuid import UUID

from app.models.database import get_db, is_db_available
from app.models.schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationListItem,
    MessageResponse
)
from app.models.chat_models import Conversation, Message
from app.services.chat_history import ChatHistoryService

router = APIRouter()


@router.get("/", response_model=List[ConversationListItem])
async def list_conversations(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all conversations"""
    # Check if database is available
    if not is_db_available():
        # Return empty list if database is not available
        return []
    
    try:
        service = ChatHistoryService(db)
        conversations = service.list_conversations(limit=limit)
        
        # Convert to list items with preview
        result = []
        for conv in conversations:
            try:
                # Get last message for preview
                messages = service.get_messages(conv.id, limit=1)
                if messages:
                    last_msg = messages[0].content
                    preview = last_msg[:100] + "..." if len(last_msg) > 100 else last_msg
                else:
                    preview = None
                
                result.append(ConversationListItem(
                    id=conv.id,
                    title=conv.title,
                    updated_at=conv.updated_at,
                    preview=preview,
                    message_count=len(conv.messages)
                ))
            except Exception as e:
                # Skip conversations that have issues
                print(f"⚠️ Warning: Could not load conversation {conv.id}: {e}")
                continue
        
        return result
    except (OperationalError, SQLAlchemyError) as e:
        # Database connection error - return empty list
        print(f"⚠️ Database error in list_conversations: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Error in list_conversations: {e}")
        # Return empty list instead of raising error
        return []


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    if not is_db_available():
        raise HTTPException(
            status_code=503,
            detail="Database not available. Please set up PostgreSQL and configure DATABASE_URL in .env"
        )
    
    try:
        service = ChatHistoryService(db)
        new_conversation = service.create_conversation(
            title=conversation.title
        )
        return ConversationResponse.model_validate(new_conversation)
    except (OperationalError, SQLAlchemyError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a conversation with all its messages"""
    try:
        service = ChatHistoryService(db)
        conversation = service.get_conversation_with_messages(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationWithMessages.model_validate(conversation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    update_data: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """Update a conversation (e.g., change title)"""
    try:
        service = ChatHistoryService(db)
        conversation = service.update_conversation(conversation_id, update_data)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationResponse.model_validate(conversation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    try:
        service = ChatHistoryService(db)
        success = service.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: UUID,
    limit: int = None,
    db: Session = Depends(get_db)
):
    """Get messages for a conversation"""
    try:
        service = ChatHistoryService(db)
        
        # Verify conversation exists
        conversation = service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = service.get_messages(conversation_id, limit=limit)
        return [MessageResponse.model_validate(msg) for msg in messages]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

