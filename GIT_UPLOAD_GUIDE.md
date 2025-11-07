# Git Upload Guide - Graph RAG Chatbot

## Current Status
✅ Project initialized with Git
✅ All files staged and committed locally
✅ Ready to push to GitHub

## To Upload to GitHub

### Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Enter repository name: **Graph-RAG-Chatbot**
3. Add description: **RAG-powered AI chatbot with chat history and document references**
4. Choose: Public or Private
5. Click "Create repository"

### Step 2: Add Remote and Push
```powershell
cd D:\GENAIPro

# Add the remote (replace YOUR_USERNAME and YOUR_REPO_URL)
git remote add origin https://github.com/YOUR_USERNAME/Graph-RAG-Chatbot.git

# Rename branch to main (optional)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 3: Alternative - Using GitHub CLI
```powershell
# If you have GitHub CLI installed
gh repo create Graph-RAG-Chatbot --source=. --remote=origin --push
```

## Project Structure
```
Graph-RAG-Chatbot/
├── app/                          # Backend (FastAPI)
│   ├── api/endpoints/           # API routes
│   ├── models/                  # SQLAlchemy models & Pydantic schemas
│   ├── services/                # Business logic (chat, RAG, history)
│   ├── core/                    # Configuration
│   └── main.py                  # FastAPI application
├── frontend/                    # Frontend (Next.js)
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── store/               # Zustand state management
│   │   ├── services/            # API client
│   │   ├── types/               # TypeScript types
│   │   └── app/                 # Next.js app directory
│   └── package.json
├── knowledge_base/              # 20 pre-loaded documents
├── docker-compose.yml           # Qdrant vector database
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── README.md                    # Main documentation
└── QUICK_START.md               # Quick start guide
```

## Git Commands Cheatsheet

```powershell
# Check status
git status

# View commits
git log --oneline

# Make changes and commit
git add .
git commit -m "Your message"
git push

# Create a new branch
git checkout -b feature/new-feature
git push -u origin feature/new-feature

# View remote
git remote -v
```

## Important Notes
- `.env` is in `.gitignore` - Never commit API keys!
- `.venv/` is in `.gitignore` - Use `requirements.txt` instead
- `node_modules/` is in `.gitignore` - Run `npm install` on clone
- `__pycache__/` is in `.gitignore` - Python cache files

## After Upload

### Cloning the Repository
```powershell
git clone https://github.com/YOUR_USERNAME/Graph-RAG-Chatbot.git
cd Graph-RAG-Chatbot

# Install dependencies
pip install -r requirements.txt
cd frontend
npm install
```

## Features Included
✅ RAG (Retrieval-Augmented Generation) with Qdrant vector database
✅ OpenRouter LLM integration with multiple models
✅ Chat history persistence (PostgreSQL)
✅ Document references and source attribution
✅ Web search integration (Brave Search API)
✅ Dark mode ChatGPT-like UI
✅ Conversation management
✅ Type-safe TypeScript frontend
✅ FastAPI backend with SQLAlchemy ORM

## Support
- See `README.md` for detailed setup instructions
- See `QUICK_START.md` for quick deployment guide
- Check `.env.example` for required environment variables

