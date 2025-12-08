"""
Migration script to add candidate_id column to applications table.
This fixes the schema mismatch between the model and database.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import engine
from app.config import settings
from sqlalchemy import text

def add_candidate_id_column():
    """Add candidate_id column to applications table if it doesn't exist."""
    
    print("🔄 Adding 'candidate_id' column to applications table...")
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Check if column already exists
                if settings.database_url.startswith("postgresql"):
                    # PostgreSQL
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='applications' AND column_name='candidate_id'
                    """))
                    if result.fetchone():
                        print("✅ Column 'candidate_id' already exists in applications table")
                        trans.rollback()
                        return
                    
                    # Check if candidates table exists
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'candidates'
                        )
                    """))
                    candidates_table_exists = result.scalar()
                    
                    if not candidates_table_exists:
                        print("⚠️  'candidates' table does not exist. Please create it first.")
                        trans.rollback()
                        return
                    
                    # Add the candidate_id column
                    print("Adding candidate_id column...")
                    conn.execute(text("""
                        ALTER TABLE applications 
                        ADD COLUMN candidate_id VARCHAR(36)
                    """))
                    
                    # Create index on candidate_id
                    print("Creating index on candidate_id...")
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_applications_candidate_id 
                        ON applications(candidate_id)
                    """))
                    
                    # Add foreign key constraint if candidates table exists
                    print("Adding foreign key constraint...")
                    try:
                        conn.execute(text("""
                            ALTER TABLE applications 
                            ADD CONSTRAINT fk_applications_candidate_id 
                            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
                        """))
                        print("✅ Foreign key constraint added")
                    except Exception as e:
                        print(f"⚠️  Could not add foreign key constraint: {e}")
                        print("   This is okay if there are existing rows. You may need to populate candidate_id first.")
                    
                    # Commit the transaction
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
    add_candidate_id_column()
    print("✅ Migration script completed!")

