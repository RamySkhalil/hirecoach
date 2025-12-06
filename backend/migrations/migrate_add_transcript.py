#!/usr/bin/env python3
"""
Database migration script to add transcript_json column.
Run this script to apply the migration manually if needed.
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.db import engine
from app.config import settings

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_transcript_column():
    """Add transcript_json column to interview_sessions table."""
    try:
        # Check if column already exists
        if check_column_exists('interview_sessions', 'transcript_json'):
            print("✅ Column 'transcript_json' already exists in 'interview_sessions' table")
            return True
        
        # Determine database type
        db_url = settings.database_url
        
        with engine.connect() as conn:
            if db_url.startswith("sqlite"):
                # SQLite doesn't support ADD COLUMN IF NOT EXISTS
                sql = "ALTER TABLE interview_sessions ADD COLUMN transcript_json TEXT"
            elif db_url.startswith("postgresql"):
                sql = "ALTER TABLE interview_sessions ADD COLUMN IF NOT EXISTS transcript_json JSON"
            elif db_url.startswith("mysql"):
                sql = "ALTER TABLE interview_sessions ADD COLUMN IF NOT EXISTS transcript_json JSON"
            else:
                print(f"⚠️  Unknown database type: {db_url}")
                return False
            
            print(f"Executing: {sql}")
            conn.execute(text(sql))
            conn.commit()
            print("✅ Successfully added 'transcript_json' column to 'interview_sessions' table")
            return True
            
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add transcript_json column")
    print("=" * 60)
    print(f"Database URL: {settings.database_url[:30]}...")
    print()
    
    success = add_transcript_column()
    
    if success:
        print()
        print("=" * 60)
        print("Migration completed successfully! ✅")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("Migration failed! ❌")
        print("=" * 60)
        sys.exit(1)

