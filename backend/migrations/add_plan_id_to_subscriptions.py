"""
Migration: Add plan_id column to subscriptions table

This migration adds the plan_id foreign key to the subscriptions table
to support the new dynamic pricing system.

Run with: python migrations/add_plan_id_to_subscriptions.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db import engine, SessionLocal
from app.models import PricingPlan, Subscription


def run_migration():
    """Run the migration to add plan_id column."""
    
    print("=" * 60)
    print("MIGRATION: Add plan_id to subscriptions table")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Step 1: Check if column already exists
            print("\n[1/5] Checking if plan_id column already exists...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='subscriptions' AND column_name='plan_id';
            """))
            
            if result.fetchone():
                print("✅ Column plan_id already exists. Skipping migration.")
                trans.rollback()
                return
            
            print("✅ Column plan_id does not exist. Proceeding with migration...")
            
            # Step 2: Add plan_id column (nullable first)
            print("\n[2/5] Adding plan_id column (nullable)...")
            conn.execute(text("""
                ALTER TABLE subscriptions 
                ADD COLUMN plan_id INTEGER;
            """))
            print("✅ Column added successfully")
            
            # Step 3: Get or create free plan
            print("\n[3/5] Getting free plan ID...")
            db = SessionLocal()
            try:
                free_plan = db.query(PricingPlan).filter_by(code='free').first()
                
                if not free_plan:
                    print("⚠️  Free plan not found. Creating it...")
                    free_plan = PricingPlan(
                        code='free',
                        name='Free',
                        description='Get started with limited access',
                        is_active=True,
                        sort_order=0
                    )
                    db.add(free_plan)
                    db.commit()
                    db.refresh(free_plan)
                    print(f"✅ Created free plan with ID: {free_plan.id}")
                else:
                    print(f"✅ Found free plan with ID: {free_plan.id}")
                
                free_plan_id = free_plan.id
                
            finally:
                db.close()
            
            # Step 4: Update existing subscriptions to use free plan
            print(f"\n[4/5] Setting plan_id={free_plan_id} for existing subscriptions...")
            result = conn.execute(text(f"""
                UPDATE subscriptions 
                SET plan_id = {free_plan_id} 
                WHERE plan_id IS NULL;
            """))
            updated_count = result.rowcount
            print(f"✅ Updated {updated_count} existing subscription(s)")
            
            # Step 5: Add foreign key constraint
            print("\n[5/5] Adding foreign key constraint...")
            conn.execute(text("""
                ALTER TABLE subscriptions 
                ADD CONSTRAINT fk_subscriptions_plan_id 
                FOREIGN KEY (plan_id) REFERENCES pricing_plans(id);
            """))
            print("✅ Foreign key constraint added")
            
            # Step 6: Add index for performance
            print("\n[6/6] Adding index on plan_id...")
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id 
                    ON subscriptions(plan_id);
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
            print(f"  - Added plan_id column to subscriptions table")
            print(f"  - Updated {updated_count} existing subscription(s) to use free plan")
            print(f"  - Added foreign key constraint to pricing_plans")
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
        print("\n[1/3] Checking plan_id column...")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name='subscriptions' AND column_name='plan_id';
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Column exists: {row[0]} ({row[1]}, nullable={row[2]})")
        else:
            print("❌ Column not found!")
            return False
        
        # Check foreign key constraint
        print("\n[2/3] Checking foreign key constraint...")
        result = conn.execute(text("""
            SELECT constraint_name, table_name, column_name
            FROM information_schema.key_column_usage
            WHERE table_name='subscriptions' AND column_name='plan_id';
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Foreign key exists: {row[0]}")
        else:
            print("⚠️  Foreign key constraint not found (may be named differently)")
        
        # Check subscriptions have plan_id set
        print("\n[3/3] Checking subscriptions...")
        result = conn.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(plan_id) as with_plan_id,
                   COUNT(*) - COUNT(plan_id) as missing_plan_id
            FROM subscriptions;
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Total subscriptions: {row[0]}")
            print(f"✅ With plan_id: {row[1]}")
            print(f"{'✅' if row[2] == 0 else '⚠️ '} Missing plan_id: {row[2]}")
        
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
        sys.exit(1)

