from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from app.core.config import get_settings

settings = get_settings()

# Initialize engine as None, will be set if connection succeeds
engine = None
SessionLocal = None
_db_available = False

try:
    # Create database engine
    engine = create_engine(
        settings.DATABASE_URL or "postgresql://postgres:postgres@localhost:5432/rag_chatbot",
        pool_pre_ping=True,
        echo=settings.DEBUG,
        connect_args={"connect_timeout": 5}
    )
    # Test connection
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    _db_available = True
    print("✅ Database connection successful")
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"⚠️ WARNING: Could not connect to database: {e}")
    print("⚠️ Chat history features will be disabled. The app will continue to work without database.")
    print("⚠️ To enable chat history, please set up PostgreSQL and update DATABASE_URL in .env")
    _db_available = False

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    if not _db_available or SessionLocal is None:
        # Return a mock session that raises an error when used
        class MockSession:
            def query(self, *args):
                raise OperationalError("Database not available", None, None)
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        yield MockSession()
        return
    
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        print(f"⚠️ Database connection error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def is_db_available():
    """Check if database is available"""
    return _db_available


def init_db():
    """Initialize database tables"""
    if engine and _db_available:
        Base.metadata.create_all(bind=engine)

