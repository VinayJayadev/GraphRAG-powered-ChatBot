# Quick Start Guide

## Using System Python (Recommended)

Since all packages are already installed in your system Python, you can run the application directly.

### 1. Start Backend

```bash
# Option 1: Direct command
python -m uvicorn app.main:app --reload

# Option 2: Use the script
.\run_backend.ps1
```

The backend will start at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### 2. Start Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

The frontend will start at: `http://localhost:3000`

### 3. Setup PostgreSQL Database (Required for Chat History)

1. **Install PostgreSQL** (if not already installed)
   - Download from: https://www.postgresql.org/download/

2. **Create Database**
   ```sql
   CREATE DATABASE rag_chatbot;
   ```

3. **Update `.env` file**
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/rag_chatbot
   ```

4. **Database tables will be created automatically** when you start the backend

### 4. Optional: Load Knowledge Base

If you want to use RAG with knowledge base documents:

1. **Start Qdrant** (vector database):
   ```bash
   docker-compose up -d qdrant
   ```

2. **Load knowledge base**:
   ```bash
   python load_knowledge_base.py
   ```

## Troubleshooting

### Database Connection Error

If you see database connection errors:
1. Check PostgreSQL is running: `psql -U postgres -c "SELECT version();"`
2. Verify database exists: `\l` in psql
3. Check `.env` file has correct `DATABASE_URL`

### Port Already in Use

If port 8000 is already in use:
```bash
# Change port in command
python -m uvicorn app.main:app --reload --port 8001
```

### Package Import Errors

If you see import errors, verify packages are installed:
```bash
python -c "import fastapi, sqlalchemy, psycopg2; print('All packages OK')"
```

## Next Steps

- Visit `http://localhost:3000` to use the chat interface
- Visit `http://localhost:8000/docs` to explore the API
- Start chatting - conversations will be saved automatically!

