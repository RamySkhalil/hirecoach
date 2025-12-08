"""
Migration script to update the applicationstatus enum to match the ApplicationStatus model.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import engine
from app.config import settings
from sqlalchemy import text

def update_application_status_enum():
    """Update the applicationstatus enum in the database."""
    
    print("🔄 Starting applicationstatus enum migration...")
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Check current enum values
                result = conn.execute(text("""
                    SELECT unnest(enum_range(NULL::applicationstatus)) as enum_value;
                """))
                existing_values = [row[0] for row in result]
                print(f"Current enum values: {existing_values}")
                
                # Expected values from ApplicationStatus enum
                expected_values = ['APPLIED', 'SCREENING', 'SHORTLISTED', 'INTERVIEW_SCHEDULED', 'OFFERED', 'REJECTED', 'HIRED']
                
                # If enum already has all expected values, we're good
                if all(val in existing_values for val in expected_values):
                    print("✅ Enum already has all expected values. No migration needed.")
                    trans.rollback()
                    return
                
                # Create new enum with all expected values
                print("⚠️  Creating new enum with expected values...")
                conn.execute(text("""
                    CREATE TYPE applicationstatus_new AS ENUM (
                        'APPLIED', 'SCREENING', 'SHORTLISTED', 'INTERVIEW_SCHEDULED', 
                        'OFFERED', 'REJECTED', 'HIRED'
                    );
                """))
                
                # Map old values to new values (handle various possible old values)
                print("Updating applications table...")
                conn.execute(text("""
                    ALTER TABLE applications 
                    ALTER COLUMN status TYPE applicationstatus_new 
                    USING CASE 
                        WHEN status::text = 'APPLIED' THEN 'APPLIED'::applicationstatus_new
                        WHEN status::text = 'SCREENING' THEN 'SCREENING'::applicationstatus_new
                        WHEN status::text = 'SHORTLISTED' THEN 'SHORTLISTED'::applicationstatus_new
                        WHEN status::text = 'INTERVIEW_SCHEDULED' THEN 'INTERVIEW_SCHEDULED'::applicationstatus_new
                        WHEN status::text = 'OFFERED' THEN 'OFFERED'::applicationstatus_new
                        WHEN status::text = 'REJECTED' THEN 'REJECTED'::applicationstatus_new
                        WHEN status::text = 'HIRED' THEN 'HIRED'::applicationstatus_new
                        WHEN status::text = 'applied' THEN 'APPLIED'::applicationstatus_new
                        WHEN status::text = 'screening' THEN 'SCREENING'::applicationstatus_new
                        WHEN status::text = 'shortlisted' THEN 'SHORTLISTED'::applicationstatus_new
                        WHEN status::text = 'pending' THEN 'APPLIED'::applicationstatus_new
                        WHEN status::text = 'reviewed' THEN 'SCREENING'::applicationstatus_new
                        ELSE 'APPLIED'::applicationstatus_new
                    END;
                """))
                
                # Drop old enum and rename new one
                print("Replacing old enum...")
                conn.execute(text("DROP TYPE applicationstatus CASCADE;"))
                conn.execute(text("ALTER TYPE applicationstatus_new RENAME TO applicationstatus;"))
                
                print("✅ Successfully updated applicationstatus enum")
                
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
    print("🔄 Starting applicationstatus enum migration...")
    update_application_status_enum()
    print("✅ Migration script completed!")

