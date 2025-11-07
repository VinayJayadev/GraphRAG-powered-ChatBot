from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import chat, conversations
from app.core.config import get_settings
from app.models.database import init_db, engine
from app.models import chat_models

settings = get_settings()

app = FastAPI(
    title="Advanced RAG Chatbot",
    description="A sophisticated chatbot using RAG, OpenRouter, and graph-based retrieval",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Customize this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    from app.models.database import engine, is_db_available
    
    if is_db_available() and engine:
        try:
            # Create tables
            ChatModelsBase.metadata.create_all(bind=engine)
            print("✅ Database tables initialized successfully")
        except Exception as e:
            print(f"⚠️ WARNING: Could not initialize database tables: {e}")
            print("⚠️ The application will continue but chat history will not be saved")
    else:
        print("⚠️ Database not available - chat history features disabled")
        print("⚠️ To enable chat history, set up PostgreSQL and configure DATABASE_URL in .env")

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
