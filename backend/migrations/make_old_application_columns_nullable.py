"""
Migration script to make old application columns nullable.
The new schema uses candidate_id instead of applicant_email/applicant_name/etc.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import engine
from app.config import settings
from sqlalchemy import text

def make_old_columns_nullable():
    """Make old application columns nullable to avoid conflicts with new schema."""
    
    print("🔄 Making old application columns nullable...")
    
    # Old columns that should be nullable (from legacy schema)
    old_columns = [
        "applicant_email",
        "applicant_name", 
        "applicant_phone",
        "user_id",
        "cv_id",
        "cover_letter",
        "portfolio_url",
        "linkedin_url",
        "recruiter_notes",
        "rejection_reason",
        "reviewed_at",
        "interview_scheduled_at",
        "interview_completed_at",
        "interview_session_id",
        "interview_score",
        "cv_match_score",
        "external_id"
    ]
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                if settings.database_url.startswith("postgresql"):
                    # Check existing columns
                    result = conn.execute(text("""
                        SELECT column_name, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name='applications'
                    """))
                    existing_columns = {row[0]: row[1] for row in result}
                    
                    # Make old columns nullable
                    for column_name in old_columns:
                        if column_name in existing_columns:
                            if existing_columns[column_name] == 'NO':
                                print(f"Making column '{column_name}' nullable...")
                                conn.execute(text(f"""
                                    ALTER TABLE applications 
                                    ALTER COLUMN {column_name} DROP NOT NULL
                                """))
                                print(f"✅ Made column '{column_name}' nullable")
                            else:
                                print(f"✅ Column '{column_name}' is already nullable")
                        else:
                            print(f"⚠️  Column '{column_name}' does not exist (skipping)")
                    
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
    make_old_columns_nullable()
    print("✅ Migration script completed!")

