"""
Migration script to convert resume_url to resume_key in candidates table.

This migration:
1. Adds resume_key column to candidates table
2. Extracts object key from existing resume_url values
3. Migrates data from resume_url to resume_key
4. Keeps resume_url for backward compatibility (can be dropped later)
"""
import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import engine
from app.config import settings
from sqlalchemy import text

def extract_object_key_from_url(url: str) -> str:
    """
    Extract object key from various URL formats.
    
    Examples:
    - https://hirecoach.r2.cloudflarestorage.com/Applicants/file.pdf -> Applicants/file.pdf
    - https://<account-id>.r2.cloudflarestorage.com/Applicants/file.pdf -> Applicants/file.pdf
    - https://custom-domain.com/Applicants/file.pdf -> Applicants/file.pdf
    - Applicants/file.pdf -> Applicants/file.pdf (already a key)
    """
    if not url:
        return None
    
    # If it's already just a key (starts with "Applicants/"), return as-is
    if url.startswith("Applicants/"):
        return url
    
    # Try to extract the path after the domain
    # Match patterns like: https://domain.com/path or https://domain.com/path/
    patterns = [
        r'https?://[^/]+/(.+)$',  # Standard URL
        r'https?://[^/]+/(.+)/$',  # URL with trailing slash
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            key = match.group(1)
            # Remove query parameters if any
            key = key.split('?')[0]
            return key
    
    # If no pattern matches, try to find "Applicants/" in the string
    if "Applicants/" in url:
        idx = url.find("Applicants/")
        return url[idx:]
    
    # If we can't extract, return None (will be set to NULL)
    return None

def migrate_resume_url_to_key():
    """Convert resume_url to resume_key in candidates table."""
    
    print("🔄 Starting migration: resume_url -> resume_key")
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                if settings.database_url.startswith("postgresql"):
                    # Step 1: Add resume_key column if it doesn't exist
                    print("Adding resume_key column...")
                    conn.execute(text("""
                        ALTER TABLE candidates 
                        ADD COLUMN IF NOT EXISTS resume_key VARCHAR(500)
                    """))
                    print("✅ Added resume_key column")
                    
                    # Step 2: Get all candidates with resume_url
                    print("Fetching candidates with resume_url...")
                    result = conn.execute(text("""
                        SELECT id, resume_url 
                        FROM candidates 
                        WHERE resume_url IS NOT NULL AND resume_url != ''
                    """))
                    candidates = result.fetchall()
                    print(f"Found {len(candidates)} candidates with resume_url")
                    
                    # Step 3: Migrate data
                    migrated_count = 0
                    skipped_count = 0
                    for candidate_id, resume_url in candidates:
                        object_key = extract_object_key_from_url(resume_url)
                        
                        if object_key:
                            # Update the candidate with the extracted key
                            conn.execute(text("""
                                UPDATE candidates 
                                SET resume_key = :key 
                                WHERE id = :id AND (resume_key IS NULL OR resume_key = '')
                            """), {"key": object_key, "id": candidate_id})
                            migrated_count += 1
                        else:
                            print(f"⚠️  Could not extract key from URL for candidate {candidate_id}: {resume_url}")
                            skipped_count += 1
                    
                    print(f"✅ Migrated {migrated_count} candidates")
                    if skipped_count > 0:
                        print(f"⚠️  Skipped {skipped_count} candidates (could not extract key)")
                    
                    # Step 4: Create index on resume_key for performance
                    print("Creating index on resume_key...")
                    try:
                        conn.execute(text("""
                            CREATE INDEX IF NOT EXISTS idx_candidates_resume_key 
                            ON candidates(resume_key)
                        """))
                        print("✅ Created index on resume_key")
                    except Exception as e:
                        print(f"⚠️  Index creation warning (may already exist): {e}")
                    
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
    print("🔄 Starting resume_url to resume_key migration...")
    migrate_resume_url_to_key()
    print("✅ Migration script completed!")

