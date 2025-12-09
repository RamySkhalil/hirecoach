"""
Database configuration and session management.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Prepare database URL and connection arguments
database_url = settings.database_url
connect_args = {}
engine_kwargs = {"echo": settings.debug}

if database_url.startswith("sqlite"):
    # SQLite needs check_same_thread=False for FastAPI
    connect_args = {"check_same_thread": False}
    
elif database_url.startswith("postgresql"):
    # For Neon Postgres, ensure SSL is enabled
    # Neon requires sslmode=require
    if "sslmode" not in database_url:
        # Append sslmode=require if not present
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"
    
    # Connection pool settings for Postgres
    engine_kwargs.update({
        "pool_pre_ping": True,  # Verify connections before using
        "pool_size": 5,  # Default connection pool size
        "max_overflow": 10,  # Max connections beyond pool_size
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "pool_reset_on_return": "commit"  # Reset connection state on return
    })

# Create engine
engine = create_engine(
    database_url,
    connect_args=connect_args,
    **engine_kwargs
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting a database session.
    Yields a session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def enable_pgvector():
    """
    Enable pgvector extension for Postgres.
    Only runs if using Postgres. Safe to call even if extension exists.
    """
    if not settings.database_url.startswith("postgresql"):
        print("[DB] Not using Postgres, skipping pgvector extension.")
        return
    
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("[DB] ✅ pgvector extension enabled successfully.")
    except Exception as e:
        print(f"[DB] ⚠️  Could not enable pgvector extension: {e}")
        print("[DB] This is normal if the extension is already enabled or not available.")


def init_db():
    """
    Initialize the database by creating all tables.
    Call this on application startup.
    """
    from app import models  # Import here to avoid circular imports
    
    # Enable pgvector extension first (for Postgres only)
    enable_pgvector()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[DB] ✅ Database tables created/verified successfully.")

