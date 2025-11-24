"""
Health check endpoints for monitoring database and service status.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.db import get_db, engine
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health_check():
    """
    Basic health check endpoint.
    Returns service status and timestamp.
    """
    return {
        "status": "ok",
        "service": "Interviewly API",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/db")
def health_check_db(db: Session = Depends(get_db)):
    """
    Database health check endpoint.
    Tests database connectivity and returns connection status.
    
    Returns:
        - status: "ok" if database is accessible
        - database: database type (postgres/sqlite)
        - timestamp: current server time
        - pgvector_enabled: whether pgvector extension is available (for Postgres)
    """
    try:
        # Test basic query
        db.execute(text("SELECT 1"))
        
        # Determine database type
        db_type = "sqlite"
        if settings.database_url.startswith("postgresql"):
            db_type = "postgres"
        
        # Check pgvector extension (only for Postgres)
        pgvector_enabled = False
        if db_type == "postgres":
            try:
                result = db.execute(text(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                ))
                pgvector_enabled = result.scalar()
            except Exception:
                pgvector_enabled = False
        
        return {
            "status": "ok",
            "database": db_type,
            "pgvector_enabled": pgvector_enabled,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": f"Database health check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/db/tables")
def health_check_db_tables(db: Session = Depends(get_db)):
    """
    List all database tables.
    Useful for verifying migrations and schema setup.
    """
    try:
        if settings.database_url.startswith("postgresql"):
            # Postgres query to list tables
            result = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
        else:
            # SQLite query to list tables
            result = db.execute(text("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """))
            tables = [row[0] for row in result]
        
        return {
            "status": "ok",
            "tables": tables,
            "table_count": len(tables),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": f"Failed to list tables: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

