"""
Migration: Add is_active column to jobs table

This migration adds the is_active boolean column to the jobs table
to allow recruiters to activate/deactivate job ads.

Run with: python migrations/add_is_active_to_jobs.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db import engine


def run_migration():
    """Run the migration to add is_active column."""
    
    print("=" * 60)
    print("MIGRATION: Add is_active to jobs table")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Step 1: Check if column already exists
            print("\n[1/4] Checking if is_active column already exists...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='jobs' AND column_name='is_active';
            """))
            
            if result.fetchone():
                print("✅ Column is_active already exists. Skipping migration.")
                trans.rollback()
                return
            
            print("✅ Column is_active does not exist. Proceeding with migration...")
            
            # Step 2: Add is_active column (nullable first, then set defaults)
            print("\n[2/4] Adding is_active column (nullable temporarily)...")
            conn.execute(text("""
                ALTER TABLE jobs 
                ADD COLUMN is_active BOOLEAN;
            """))
            print("✅ Column added successfully")
            
            # Step 3: Set default value to True for existing jobs
            print("\n[3/4] Setting is_active=True for existing jobs...")
            result = conn.execute(text("""
                UPDATE jobs 
                SET is_active = TRUE 
                WHERE is_active IS NULL;
            """))
            updated_count = result.rowcount
            print(f"✅ Updated {updated_count} existing job(s) to is_active=TRUE")
            
            # Step 4: Make column NOT NULL with default
            print("\n[4/4] Making is_active NOT NULL with default TRUE...")
            conn.execute(text("""
                ALTER TABLE jobs 
                ALTER COLUMN is_active SET DEFAULT TRUE,
                ALTER COLUMN is_active SET NOT NULL;
            """))
            print("✅ Column set to NOT NULL with default TRUE")
            
            # Step 5: Add index for performance
            print("\n[5/5] Adding index on is_active...")
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_jobs_is_active 
                    ON jobs(is_active);
                """))
                print("✅ Index created")
            except Exception as e:
                print(f"⚠️  Index may already exist: {e}")
            
            # Commit transaction
            trans.commit()
            print("\n" + "=" * 60)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"\nSummary:")
            print(f"  - Added is_active column to jobs table")
            print(f"  - Updated {updated_count} existing job(s) to is_active=TRUE")
            print(f"  - Set column to NOT NULL with default TRUE")
            print(f"  - Added index for performance")
            print(f"\nYou can now restart your backend server.")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ MIGRATION FAILED: {e}")
            print("\nRolling back changes...")
            raise


def verify_migration():
    """Verify the migration was successful."""
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Check column exists
        print("\n[1/3] Checking is_active column...")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name='jobs' AND column_name='is_active';
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Column exists: {row[0]} ({row[1]}, nullable={row[2]}, default={row[3]})")
        else:
            print("❌ Column not found!")
            return False
        
        # Check index exists
        print("\n[2/3] Checking index...")
        result = conn.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename='jobs' AND indexname='idx_jobs_is_active';
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Index exists: {row[0]}")
        else:
            print("⚠️  Index not found (may not be critical)")
        
        # Check jobs have is_active set
        print("\n[3/3] Checking jobs...")
        result = conn.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active,
                   COUNT(CASE WHEN is_active = FALSE THEN 1 END) as inactive
            FROM jobs;
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Total jobs: {row[0]}")
            print(f"✅ Active jobs: {row[1]}")
            print(f"✅ Inactive jobs: {row[2]}")
        
        print("\n" + "=" * 60)
        print("✅ VERIFICATION COMPLETE")
        print("=" * 60)
        return True


if __name__ == "__main__":
    try:
        run_migration()
        verify_migration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

