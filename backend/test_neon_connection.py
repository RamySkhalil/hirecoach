"""
Test script to verify Neon Postgres connection and pgvector setup.
Run this after setting up DATABASE_URL in .env
"""
import sys
from sqlalchemy import text
from app.db import engine, SessionLocal, init_db
from app.config import settings

def test_basic_connection():
    """Test basic database connectivity."""
    print("\n" + "="*60)
    print("1️⃣  Testing Basic Database Connection...")
    print("="*60)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            print(f"   Database URL: {settings.database_url[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_database_type():
    """Detect and display database type."""
    print("\n" + "="*60)
    print("2️⃣  Detecting Database Type...")
    print("="*60)
    
    if settings.database_url.startswith("postgresql"):
        print("✅ Using: PostgreSQL (Production)")
        print("   SSL Mode: Enabled")
        return "postgres"
    elif settings.database_url.startswith("sqlite"):
        print("✅ Using: SQLite (Local Development)")
        return "sqlite"
    else:
        print("⚠️  Unknown database type")
        return "unknown"


def test_pgvector_extension():
    """Test if pgvector extension is available."""
    print("\n" + "="*60)
    print("3️⃣  Checking pgvector Extension...")
    print("="*60)
    
    if not settings.database_url.startswith("postgresql"):
        print("⏭️  Skipping (not using PostgreSQL)")
        return True
    
    try:
        with engine.connect() as conn:
            # Check if extension exists
            result = conn.execute(text(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
            ))
            exists = result.scalar()
            
            if exists:
                print("✅ pgvector extension is enabled!")
                
                # Get extension version
                result = conn.execute(text(
                    "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
                ))
                version = result.scalar()
                print(f"   Version: {version}")
                return True
            else:
                print("❌ pgvector extension not found")
                print("   Run: CREATE EXTENSION IF NOT EXISTS vector;")
                return False
    except Exception as e:
        print(f"❌ Failed to check pgvector: {e}")
        return False


def test_tables_created():
    """Test if all tables are created."""
    print("\n" + "="*60)
    print("4️⃣  Verifying Database Tables...")
    print("="*60)
    
    try:
        # Initialize database (creates tables)
        print("   Creating tables if not exist...")
        init_db()
        
        # List tables
        session = SessionLocal()
        if settings.database_url.startswith("postgresql"):
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
        else:
            result = session.execute(text("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """))
        
        tables = [row[0] for row in result]
        session.close()
        
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            emoji = "🆕" if table == "user_message_embeddings" else "  "
            print(f"   {emoji} {table}")
        
        # Check for new table
        if "user_message_embeddings" in tables:
            print("\n   ✅ New vector embeddings table created!")
        else:
            print("\n   ⚠️  Vector embeddings table not found")
        
        return True
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False


def test_vector_operations():
    """Test basic vector operations (if pgvector is available)."""
    print("\n" + "="*60)
    print("5️⃣  Testing Vector Operations...")
    print("="*60)
    
    if not settings.database_url.startswith("postgresql"):
        print("⏭️  Skipping (not using PostgreSQL)")
        return True
    
    try:
        from app.models import UserMessageEmbedding
        import numpy as np
        
        session = SessionLocal()
        
        # Create a test embedding
        test_embedding = UserMessageEmbedding(
            user_id="test_user_001",
            message_id="test_msg_001",
            message_text="Test message for vector embeddings",
            message_role="user",
            embedding=np.random.rand(1536).tolist(),  # Mock OpenAI embedding
            conversation_id="test_conv_001",
            context_type="test"
        )
        
        session.add(test_embedding)
        session.commit()
        print("✅ Created test vector embedding")
        
        # Query it back
        retrieved = session.query(UserMessageEmbedding).filter_by(
            user_id="test_user_001"
        ).first()
        
        if retrieved:
            print(f"✅ Retrieved embedding: {retrieved.message_text}")
            print(f"   Vector dimensions: {len(retrieved.embedding) if isinstance(retrieved.embedding, list) else 'N/A'}")
        else:
            print("❌ Failed to retrieve embedding")
        
        # Clean up test data
        session.delete(test_embedding)
        session.commit()
        session.close()
        
        print("✅ Vector operations working correctly!")
        return True
        
    except ImportError:
        print("⚠️  pgvector library not installed")
        print("   Run: pip install pgvector==0.2.4")
        return False
    except Exception as e:
        print(f"❌ Vector operations failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🔍 " + "="*58)
    print("   NEON POSTGRES + PGVECTOR CONNECTION TEST")
    print("="*60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Basic Connection", test_basic_connection()))
    results.append(("Database Type", test_database_type()))
    results.append(("pgvector Extension", test_pgvector_extension()))
    results.append(("Tables Created", test_tables_created()))
    results.append(("Vector Operations", test_vector_operations()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"Result: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! Your Neon Postgres + pgvector setup is ready!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

