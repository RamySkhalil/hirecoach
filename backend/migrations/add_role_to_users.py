"""
Migration script to add 'role' column to users table.
Run this once to update your database schema.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import engine, Base
from app.config import settings
from sqlalchemy import text

def add_role_column():
    """Add role column to users table if it doesn't exist."""
    
    print("🔄 Adding 'role' column to users table...")
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            if settings.database_url.startswith("postgresql"):
                # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='role'
                """))
                if result.fetchone():
                    print("✅ Column 'role' already exists in users table")
                    return
                
                # Add the column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR(20)
                """))
                
                # Create index on role column
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_role ON users(role)
                """))
                
            elif settings.database_url.startswith("sqlite"):
                # SQLite
                result = conn.execute(text("""
                    PRAGMA table_info(users)
                """))
                columns = [row[1] for row in result.fetchall()]
                if 'role' in columns:
                    print("✅ Column 'role' already exists in users table")
                    return
                
                # SQLite doesn't support ALTER TABLE ADD COLUMN easily
                # We'll need to recreate the table (for development only)
                print("⚠️  SQLite detected. For production, use PostgreSQL.")
                print("⚠️  SQLite requires table recreation. This will lose data!")
                print("⚠️  Consider migrating to PostgreSQL or backing up your data first.")
                
                # For SQLite, we'll just note that init_db() should handle it
                # when tables are recreated
                print("ℹ️  Run: python -c 'from app.db import init_db; init_db()' to recreate tables")
                return
            
            conn.commit()
            print("✅ Successfully added 'role' column to users table")
            
    except Exception as e:
        print(f"❌ Error adding role column: {e}")
        raise


if __name__ == "__main__":
    add_role_column()

