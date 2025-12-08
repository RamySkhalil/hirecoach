"""
Migration script to fix the job_id foreign key constraint in applications table.
The constraint is pointing to job_postings but should point to jobs.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import engine
from app.config import settings
from sqlalchemy import text

def fix_job_foreign_key():
    """Fix the job_id foreign key to point to jobs table instead of job_postings."""
    
    print("🔄 Fixing job_id foreign key constraint...")
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                if settings.database_url.startswith("postgresql"):
                    # Check if the wrong foreign key exists
                    result = conn.execute(text("""
                        SELECT conname, confrelid::regclass
                        FROM pg_constraint 
                        WHERE conrelid = 'applications'::regclass 
                        AND contype = 'f' 
                        AND conname LIKE '%job%'
                    """))
                    fk_info = result.fetchall()
                    
                    if fk_info:
                        for fk_name, ref_table in fk_info:
                            print(f"Found foreign key '{fk_name}' pointing to '{ref_table}'")
                            
                            if ref_table == 'job_postings':
                                print(f"⚠️  Foreign key '{fk_name}' points to wrong table 'job_postings'")
                                print(f"   Dropping old constraint...")
                                
                                # Drop the old foreign key
                                conn.execute(text(f"""
                                    ALTER TABLE applications 
                                    DROP CONSTRAINT IF EXISTS {fk_name}
                                """))
                                print(f"✅ Dropped old constraint '{fk_name}'")
                                
                                # Check if jobs table exists
                                result = conn.execute(text("""
                                    SELECT EXISTS (
                                        SELECT FROM information_schema.tables 
                                        WHERE table_name = 'jobs'
                                    )
                                """))
                                jobs_exists = result.scalar()
                                
                                if jobs_exists:
                                    # Add new foreign key pointing to jobs table
                                    print("Adding new foreign key to 'jobs' table...")
                                    conn.execute(text("""
                                        ALTER TABLE applications 
                                        ADD CONSTRAINT applications_job_id_fkey 
                                        FOREIGN KEY (job_id) REFERENCES jobs(id)
                                    """))
                                    print("✅ Added new foreign key to 'jobs' table")
                                else:
                                    print("⚠️  'jobs' table does not exist. Cannot add foreign key.")
                            elif ref_table == 'jobs':
                                print(f"✅ Foreign key '{fk_name}' already points to correct table 'jobs'")
                    else:
                        print("⚠️  No job-related foreign key found. Adding new one...")
                        
                        # Check if jobs table exists
                        result = conn.execute(text("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = 'jobs'
                            )
                        """))
                        jobs_exists = result.scalar()
                        
                        if jobs_exists:
                            # Add foreign key pointing to jobs table
                            print("Adding foreign key to 'jobs' table...")
                            try:
                                conn.execute(text("""
                                    ALTER TABLE applications 
                                    ADD CONSTRAINT applications_job_id_fkey 
                                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                                """))
                                print("✅ Added foreign key to 'jobs' table")
                            except Exception as e:
                                if "already exists" in str(e).lower():
                                    print("✅ Foreign key already exists")
                                else:
                                    raise
                        else:
                            print("⚠️  'jobs' table does not exist. Cannot add foreign key.")
                    
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
    print("🔄 Starting applications foreign key migration...")
    fix_job_foreign_key()
    print("✅ Migration script completed!")

