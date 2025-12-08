"""
Migration script to update the jobstatus enum to include OPEN and use uppercase values.
This fixes the mismatch between the code (using uppercase OPEN) and the database enum.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings

def update_job_status_enum():
    """Update the jobstatus enum in the database."""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()
        try:
            # First, check if the enum exists and what values it has
            result = conn.execute(text("""
                SELECT unnest(enum_range(NULL::jobstatus)) as enum_value;
            """))
            existing_values = [row[0] for row in result]
            print(f"Current enum values: {existing_values}")
            
            # If the enum already has OPEN, we're good
            if 'OPEN' in existing_values:
                print("✅ Enum already has OPEN value. No migration needed.")
                trans.rollback()
                return
            
            # If we have ACTIVE instead of OPEN, replace it
            if 'ACTIVE' in existing_values:
                print("⚠️  Found ACTIVE value. Replacing with OPEN...")
                
                # Create a new enum type with OPEN instead of ACTIVE
                conn.execute(text("""
                    CREATE TYPE jobstatus_new AS ENUM ('DRAFT', 'OPEN', 'PAUSED', 'CLOSED');
                """))
                
                # Update all existing jobs to use the new enum
                # Map ACTIVE to OPEN
                # First, update jobs table if it exists
                try:
                    conn.execute(text("""
                        ALTER TABLE jobs 
                        ALTER COLUMN status TYPE jobstatus_new 
                        USING CASE 
                            WHEN status::text = 'DRAFT' THEN 'DRAFT'::jobstatus_new
                            WHEN status::text = 'ACTIVE' THEN 'OPEN'::jobstatus_new
                            WHEN status::text = 'PAUSED' THEN 'PAUSED'::jobstatus_new
                            WHEN status::text = 'CLOSED' THEN 'CLOSED'::jobstatus_new
                            ELSE 'DRAFT'::jobstatus_new
                        END;
                    """))
                    print("✅ Updated jobs table")
                except Exception as e:
                    print(f"⚠️  jobs table not found or already updated: {e}")
                
                # Update job_postings table if it exists
                try:
                    conn.execute(text("""
                        ALTER TABLE job_postings 
                        ALTER COLUMN status TYPE jobstatus_new 
                        USING CASE 
                            WHEN status::text = 'DRAFT' THEN 'DRAFT'::jobstatus_new
                            WHEN status::text = 'ACTIVE' THEN 'OPEN'::jobstatus_new
                            WHEN status::text = 'PAUSED' THEN 'PAUSED'::jobstatus_new
                            WHEN status::text = 'CLOSED' THEN 'CLOSED'::jobstatus_new
                            ELSE 'DRAFT'::jobstatus_new
                        END;
                    """))
                    print("✅ Updated job_postings table")
                except Exception as e:
                    print(f"⚠️  job_postings table not found or already updated: {e}")
                
                # Drop the old enum and rename the new one
                conn.execute(text("DROP TYPE jobstatus CASCADE;"))
                conn.execute(text("ALTER TYPE jobstatus_new RENAME TO jobstatus;"))
                
                print("✅ Successfully replaced ACTIVE with OPEN in jobstatus enum")
                trans.commit()
                return
            
            # If we have lowercase values, we need to update them
            if 'active' in existing_values or 'draft' in existing_values:
                print("⚠️  Found lowercase enum values. Updating to uppercase...")
                
                # Create a new enum type with uppercase values
                conn.execute(text("""
                    CREATE TYPE jobstatus_new AS ENUM ('DRAFT', 'OPEN', 'PAUSED', 'CLOSED');
                """))
                
                # Update all existing jobs to use the new enum
                # Map old values to new values
                # First, update jobs table if it exists
                try:
                    conn.execute(text("""
                        ALTER TABLE jobs 
                        ALTER COLUMN status TYPE jobstatus_new 
                        USING CASE 
                            WHEN status::text = 'draft' THEN 'DRAFT'::jobstatus_new
                            WHEN status::text = 'active' THEN 'OPEN'::jobstatus_new
                            WHEN status::text = 'paused' THEN 'PAUSED'::jobstatus_new
                            WHEN status::text = 'closed' THEN 'CLOSED'::jobstatus_new
                            ELSE 'DRAFT'::jobstatus_new
                        END;
                    """))
                    print("✅ Updated jobs table")
                except Exception as e:
                    print(f"⚠️  jobs table not found or already updated: {e}")
                
                # Update job_postings table if it exists
                try:
                    conn.execute(text("""
                        ALTER TABLE job_postings 
                        ALTER COLUMN status TYPE jobstatus_new 
                        USING CASE 
                            WHEN status::text = 'draft' THEN 'DRAFT'::jobstatus_new
                            WHEN status::text = 'active' THEN 'OPEN'::jobstatus_new
                            WHEN status::text = 'paused' THEN 'PAUSED'::jobstatus_new
                            WHEN status::text = 'closed' THEN 'CLOSED'::jobstatus_new
                            ELSE 'DRAFT'::jobstatus_new
                        END;
                    """))
                    print("✅ Updated job_postings table")
                except Exception as e:
                    print(f"⚠️  job_postings table not found or already updated: {e}")
                
                # Drop the old enum and rename the new one
                conn.execute(text("DROP TYPE jobstatus CASCADE;"))
                conn.execute(text("ALTER TYPE jobstatus_new RENAME TO jobstatus;"))
                
                print("✅ Successfully updated jobstatus enum to uppercase values with OPEN")
            
            # Commit the transaction
            trans.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error during migration: {e}")
            raise

if __name__ == "__main__":
    print("🔄 Starting jobstatus enum migration...")
    update_job_status_enum()
    print("✅ Migration script completed!")

