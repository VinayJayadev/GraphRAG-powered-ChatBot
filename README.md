# Advanced RAG Chatbot with OpenRouter

A sophisticated conversational AI system that implements advanced RAG (Retrieval Augmented Generation) techniques using OpenRouter's LLM API, vector databases, graph-based retrieval, and web search capabilities.

## Features

- **Advanced RAG Implementation**: Hybrid search with semantic embeddings
- **Graph-based Document Relationships**: Enhanced context retrieval using graph structures
- **Semantic Search**: Using sentence transformers for intelligent document retrieval
- **Vector Storage**: Qdrant vector database for efficient similarity search (optional)
- **Multiple LLM Models**: Access to various AI models through OpenRouter API
- **Web Search Integration**: Real-time web search using Brave Search API for current information
- **FastAPI Backend**: Async support with comprehensive error handling
- **Modern Frontend**: Clean and responsive Next.js chat interface
- **Dockerized Deployment**: Easy setup with Docker Compose
- **Tool Integration**: Custom tools for enhanced functionality

## Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- Docker and Docker Compose (optional, for Qdrant)
- OpenRouter API key
- Brave Search API key (optional, for web search)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd GENAIPro
```

### 2. Environment Setup

**Important**: Never commit your `.env` file to git! It contains sensitive API keys.

Create a `.env` file in the root directory (you can copy from `.env.example` if it exists):

```bash
# Copy the example file (if it doesn't exist, create it manually)
cp .env.example .env
```

Then edit `.env` and add your actual API keys:

```env
# API Keys
OPENROUTER_API_KEY="sk-or-v1-your-actual-openrouter-api-key"
BRAVE_API_KEY="BSA-your-actual-brave-api-key"  # Optional, for web search

# Vector Database (Optional - app works without Qdrant)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Server Settings
PORT=8000
HOST=0.0.0.0
DEBUG=True
```

**Getting API Keys:**
- **OpenRouter**: Sign up at [OpenRouter.ai](https://openrouter.ai) and get your API key
- **Brave Search**: Sign up at [Brave Search API](https://api.search.brave.com/) and get your API key (optional)

**Security Note**: The `.env` file is automatically ignored by git (via `.gitignore`). Never commit real API keys to the repository.

### 3. Install Dependencies

**Backend:**

If you have a virtual environment (`.venv` or `venv`), activate it first:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Or use the venv Python directly
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If you don't have a virtual environment or want to create one:

```bash
# Create virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**Alternative:** Use the setup script:
```bash
# Windows PowerShell
.\setup_venv.ps1
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 4. Start Qdrant (Optional)

If you want to use the knowledge base features, start Qdrant:

```bash
docker-compose up -d qdrant
```

**Note**: The application will work without Qdrant, but knowledge base search will return empty results. The app gracefully handles missing Qdrant connections.

### 5. Load Knowledge Base (Optional)

If Qdrant is running, load your knowledge base documents:

```bash
python load_knowledge_base.py
```

This will load all `.txt` files from the `knowledge_base/` directory into the vector store.

### 6. Run the Application

**Backend:**

If using virtual environment:
```bash
# Activate venv first
.venv\Scripts\Activate.ps1

# Then run
uvicorn app.main:app --reload
```

Or use the venv Python directly:
```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Or use the provided script:
```bash
.\run_backend.ps1
```

The backend will be available at `http://localhost:8000`

**Frontend (in a new terminal):**
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key for LLM access |
| `BRAVE_API_KEY` | No | Brave Search API key for web search features |
| `QDRANT_URL` | No | Qdrant server URL (default: `http://localhost:6333`) |
| `QDRANT_API_KEY` | No | Qdrant API key (if using cloud Qdrant) |
| `PORT` | No | Server port (default: `8000`) |
| `HOST` | No | Server host (default: `0.0.0.0`) |
| `DEBUG` | No | Debug mode (default: `False`) |

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── chat.py          # Chat API endpoints
│   ├── core/
│   │   ├── config.py            # Configuration settings
│   │   └── security.py          # Security utilities
│   ├── services/
│   │   ├── rag/
│   │   │   └── graph_rag.py     # Graph-based RAG implementation
│   │   ├── chat.py              # Chat service with RAG
│   │   ├── vector_store.py      # Vector database interface
│   │   ├── tool_service.py      # Tool execution service
│   │   └── tool_gateway.py      # Tool gateway for routing
│   └── main.py                  # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js app directory
│   │   ├── components/          # React components
│   │   ├── store/               # State management
│   │   └── types/               # TypeScript types
│   └── package.json
├── knowledge_base/              # Knowledge base documents (.txt files)
├── load_knowledge_base.py       # Script to load KB into Qdrant
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Docker image definition
├── requirements.txt             # Python dependencies
└── README.md
```

## Advanced RAG Features

- **Hybrid Search**: Combining dense vector search with metadata filtering
- **Graph-based Document Relationships**: Semantic connections between documents for enhanced context
- **Dynamic Context Enhancement**: Graph traversal to find related documents
- **Re-ranking**: Intelligent document ranking based on relevance
- **Semantic Chunking**: Intelligent text splitting with overlap
- **Web Search Integration**: Automatic web search for current information
- **Error Handling**: Graceful degradation when services are unavailable

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main Endpoints

- `POST /api/chat` - Chat with the RAG system
- `POST /api/tool` - Execute a tool
- `GET /api/tools` - List available tools

## Docker Deployment

### Full Stack Deployment

```bash
docker-compose up -d
```

This will start both the application and Qdrant.

### Qdrant Only

```bash
docker-compose up -d qdrant
```

## Usage

### Basic Chat

The chatbot can answer questions using:
1. **Knowledge Base** (if Qdrant is running and loaded)
2. **Web Search** (if Brave API key is configured)
3. **LLM Knowledge** (always available)

### Knowledge Base

Place your `.txt` files in the `knowledge_base/` directory and run:
```bash
python load_knowledge_base.py
```

### Web Search

The system automatically triggers web search for queries containing keywords like:
- "current", "latest", "today", "recent"
- "2024", "2025", "breaking", "news"
- "more", "additional", "expand", "details"

## Troubleshooting

### Qdrant Connection Issues

If you see warnings about Qdrant:
- The app will still work, but without knowledge base search
- Start Qdrant: `docker-compose up -d qdrant`
- Check Docker is running: `docker ps`

### API Key Issues

- **OpenRouter**: Ensure your API key is valid and has credits
- **Brave Search**: Web search will be skipped if not configured

### Frontend Connection Issues

- Ensure the backend is running on `http://localhost:8000`
- Check CORS settings in `app/main.py`
- Verify the frontend API URL in `frontend/src/components/ChatWindow.tsx`

## Development

### Running in Development Mode

Backend auto-reloads on code changes:
```bash
uvicorn app.main:app --reload
```

Frontend hot-reloads on code changes:
```bash
cd frontend
npm run dev
```

### Testing

Test the API directly:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "chat_history": []}'
```

## Security Best Practices

⚠️ **Important Security Notes:**

1. **Never commit API keys**: The `.env` file is automatically excluded from git via `.gitignore`
2. **Use environment variables**: All API keys are loaded from environment variables, never hardcoded
3. **Rotate keys if exposed**: If you accidentally commit a key, immediately rotate it in the provider's dashboard
4. **Use `.env.example`**: Share the template file (`.env.example`) but never the actual `.env` file
5. **Review before committing**: Always run `git status` before committing to ensure `.env` is not included

### Verifying Security

To verify your `.env` file is not being tracked by git:

```bash
# Check if .env is in git (should show nothing)
git ls-files | grep .env

# Verify .gitignore is working
git status
```

If `.env` appears in the output, it means it was committed before `.gitignore` was added. You'll need to remove it from git history (but keep the local file):

```bash
# Remove from git but keep local file
git rm --cached .env
git commit -m "Remove .env from git tracking"
```

## License

MIT

## Additional Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Brave Search API Docs](https://api.search.brave.com/app/dashboard/api-endpoints)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
