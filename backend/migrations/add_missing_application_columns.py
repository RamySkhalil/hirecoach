"""
Migration script to add missing columns to applications table.
Adds: source, applied_at, fit_score, ai_interview_score, notes
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import engine
from app.config import settings
from sqlalchemy import text

def add_missing_columns():
    """Add missing columns to applications table."""
    
    print("🔄 Adding missing columns to applications table...")
    
    columns_to_add = [
        ("source", "VARCHAR(50)", "NULL"),
        ("applied_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP"),
        ("fit_score", "FLOAT", "NULL"),
        ("ai_interview_score", "FLOAT", "NULL"),
        ("notes", "TEXT", "NULL"),
    ]
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                if settings.database_url.startswith("postgresql"):
                    # Check existing columns
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='applications'
                    """))
                    existing_columns = {row[0] for row in result}
                    
                    # Add missing columns
                    for column_name, column_type, default in columns_to_add:
                        if column_name not in existing_columns:
                            print(f"Adding column '{column_name}'...")
                            if default.startswith("DEFAULT"):
                                conn.execute(text(f"""
                                    ALTER TABLE applications 
                                    ADD COLUMN {column_name} {column_type} {default}
                                """))
                            else:
                                conn.execute(text(f"""
                                    ALTER TABLE applications 
                                    ADD COLUMN {column_name} {column_type}
                                """))
                            print(f"✅ Added column '{column_name}'")
                        else:
                            print(f"✅ Column '{column_name}' already exists")
                    
                    # Check if status column exists and is the right type
                    result = conn.execute(text("""
                        SELECT data_type 
                        FROM information_schema.columns 
                        WHERE table_name='applications' AND column_name='status'
                    """))
                    status_type = result.scalar()
                    
                    if status_type and status_type != 'USER-DEFINED':
                        print("⚠️  Status column exists but may not be enum type. This is okay if it's a string.")
                    
                    trans.commit()
                    print("✅ Migration completed successfully!")
                    
            except Exception as e:
                trans.rollback()
                print(f"❌ Error during migration: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise

if __name__ == "__main__":
    print("🔄 Starting applications table migration...")
    add_missing_columns()
    print("✅ Migration script completed!")

