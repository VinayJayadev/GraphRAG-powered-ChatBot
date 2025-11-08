from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel
import os

from app.services.chat import ChatService
from app.models.database import get_db, is_db_available
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_history import ChatHistoryService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(lambda: ChatService()),
    db: Session = Depends(get_db)
):
    """
    Chat endpoint that uses RAG and OpenRouter with tool execution for generating responses.
    Saves messages to database if conversation_id is provided.
    """
    try:
        # Check if database is available
        db_available = is_db_available()
        conversation_id = request.conversation_id
        chat_history = request.chat_history  # Default to provided history
        
        # Only use database if available
        if db_available:
            try:
                history_service = ChatHistoryService(db)
                
                # Get or create conversation
                if not conversation_id:
                    # Create new conversation with title from first message
                    title = history_service.generate_conversation_title(request.message)
                    conversation = history_service.create_conversation(title=title)
                    conversation_id = conversation.id
                
                # Get existing messages from database if conversation exists
                if conversation_id:
                    try:
                        existing_messages = history_service.get_messages(conversation_id)
                        # Convert to chat_history format for LLM context
                        if existing_messages:
                            chat_history = []
                            i = 0
                            while i < len(existing_messages):
                                if existing_messages[i].role.value == "user":
                                    user_msg = existing_messages[i].content
                                    assistant_msg = None
                                    # Look for corresponding assistant message
                                    if i + 1 < len(existing_messages) and existing_messages[i + 1].role.value == "assistant":
                                        assistant_msg = existing_messages[i + 1].content
                                        i += 2
                                    else:
                                        i += 1
                                    chat_history.append({
                                        "user": user_msg,
                                        "assistant": assistant_msg
                                    })
                                else:
                                    i += 1
                    except Exception as e:
                        print(f"⚠️ WARNING: Could not load conversation history: {e}")
                        # Continue with provided chat_history
            except (OperationalError, SQLAlchemyError) as e:
                print(f"⚠️ WARNING: Database error, continuing without chat history: {e}")
                # Continue without database
                db_available = False
        
        # Get response from chat service
        response = await chat_service.get_response(
            query=request.message,
            chat_history=chat_history
        )
        
        # Save messages to database if available
        if db_available and conversation_id:
            try:
                history_service = ChatHistoryService(db)
                # Save user message
                history_service.add_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=request.message
                )
                
                # Save assistant message with sources in metadata
                history_service.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response["response"],
                    metadata={
                        "sources": response.get("sources", []),
                        "rag_metadata": response.get("metadata", {})
                    }
                )
            except Exception as e:
                print(f"⚠️ WARNING: Could not save messages to database: {e}")
                # Continue even if saving fails
        
        # Add conversation_id to response (use a placeholder UUID if DB not available)
        if not conversation_id:
            import uuid
            conversation_id = uuid.uuid4()  # Generate a temporary ID
        response["conversation_id"] = conversation_id
        
        return ChatResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ToolRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

class ToolResponse(BaseModel):
    result: str
    tool: str

@router.post("/tool", response_model=ToolResponse)
async def execute_tool(request: ToolRequest, chat_service: ChatService = Depends(lambda: ChatService())):
    """
    Execute a tool.
    """
    try:
        result = await chat_service.tool_gateway.execute_tool(
            tool_name=request.tool,
            arguments=request.arguments
        )
        
        if result is None:
            raise HTTPException(status_code=400, detail="Tool execution failed")
        
        return ToolResponse(
            result=result,
            tool=request.tool
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools")
def get_available_tools(chat_service: ChatService = Depends(lambda: ChatService())):
    """
    Get list of available tools.
    """
    try:
        tools = chat_service.tool_gateway.get_available_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base/{filename}")
async def get_knowledge_base_file(filename: str):
    """
    Get the content of a knowledge base file by filename.
    Returns the file content as plain text.
    """
    try:
        # Security: Validate filename to prevent directory traversal
        # Remove .txt extension for validation
        base_name = filename.replace('.txt', '') if filename.endswith('.txt') else filename
        
        # Check if base name contains only safe characters (alphanumeric, underscores, hyphens)
        if not all(c.isalnum() or c in ('_', '-') for c in base_name):
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Ensure filename ends with .txt
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        
        # Additional security: prevent directory traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Get the knowledge base directory path
        # Try multiple methods to find the project root and knowledge_base directory
        kb_dir = None
        searched_paths = []
        
        # Method 1: Calculate from __file__ location
        # __file__ is at: app/api/endpoints/chat.py
        # We need to go up 4 levels to get to project root: endpoints -> api -> app -> project_root
        try:
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            kb_dir_candidate = os.path.join(project_root, 'knowledge_base')
            searched_paths.append(kb_dir_candidate)
            if os.path.exists(kb_dir_candidate):
                kb_dir = kb_dir_candidate
        except Exception as e:
            print(f"WARNING: Could not determine KB path from __file__: {e}")
        
        # Method 2: Try relative to current working directory
        if not kb_dir:
            try:
                cwd = os.getcwd()
                # Check if knowledge_base exists in current directory
                kb_dir_candidate = os.path.join(cwd, 'knowledge_base')
                searched_paths.append(kb_dir_candidate)
                if os.path.exists(kb_dir_candidate):
                    kb_dir = kb_dir_candidate
                # Check if we're in app/ directory
                elif os.path.basename(cwd) == 'app':
                    kb_dir_candidate = os.path.join(os.path.dirname(cwd), 'knowledge_base')
                    searched_paths.append(kb_dir_candidate)
                    if os.path.exists(kb_dir_candidate):
                        kb_dir = kb_dir_candidate
            except Exception as e:
                print(f"WARNING: Could not determine KB path from CWD: {e}")
        
        # If still not found, raise an error with helpful information
        if not kb_dir:
            error_msg = f"Knowledge base directory not found. Searched in: {', '.join(searched_paths)}"
            print(f"ERROR: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        file_path = os.path.join(kb_dir, filename)
        
        # Security: Ensure the file is within the knowledge_base directory
        kb_dir_abs = os.path.abspath(kb_dir)
        file_path_abs = os.path.abspath(file_path)
        if not file_path_abs.startswith(kb_dir_abs):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Check if file exists
        if not os.path.exists(file_path):
            # Provide more detailed error information for debugging
            error_detail = f"File not found: {filename}"
            error_detail += f" | Searched in: {kb_dir_abs}"
            error_detail += f" | Full path: {file_path_abs}"
            error_detail += f" | KB dir exists: {os.path.exists(kb_dir_abs)}"
            if os.path.exists(kb_dir_abs):
                # List available files for debugging
                try:
                    available_files = [f for f in os.listdir(kb_dir_abs) if f.endswith('.txt')]
                    error_detail += f" | Available files: {', '.join(available_files[:5])}"
                except:
                    pass
            print(f"ERROR: {error_detail}")  # Log to server console
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Read and return file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "filename": filename,
            "content": content,
            "topic": filename.replace('.txt', '').replace('_', ' ').title()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
