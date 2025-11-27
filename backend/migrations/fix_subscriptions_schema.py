"""
Migration: Fix subscriptions table schema

This migration adds missing columns to match the Subscription model:
- billing_period (required for monthly/yearly billing)
- stripe_price_id (rename from price_id)

Run with: python migrations/fix_subscriptions_schema.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db import engine, SessionLocal


def run_migration():
    """Run the migration to fix subscriptions schema."""
    
    print("=" * 60)
    print("MIGRATION: Fix subscriptions table schema")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Step 1: Check if billing_period exists
            print("\n[1/4] Checking billing_period column...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='subscriptions' AND column_name='billing_period';
            """))
            
            if result.fetchone():
                print("✅ billing_period already exists")
            else:
                print("⚠️  billing_period missing. Adding it...")
                conn.execute(text("""
                    ALTER TABLE subscriptions 
                    ADD COLUMN billing_period VARCHAR(20) DEFAULT 'monthly';
                """))
                print("✅ billing_period column added")
            
            # Step 2: Update existing rows to have billing_period
            print("\n[2/4] Setting billing_period for existing subscriptions...")
            result = conn.execute(text("""
                UPDATE subscriptions 
                SET billing_period = 'monthly' 
                WHERE billing_period IS NULL;
            """))
            updated_count = result.rowcount
            print(f"✅ Updated {updated_count} subscription(s)")
            
            # Step 3: Check if stripe_price_id exists
            print("\n[3/4] Checking stripe_price_id column...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='subscriptions' AND column_name='stripe_price_id';
            """))
            
            if result.fetchone():
                print("✅ stripe_price_id already exists")
            else:
                # Check if old price_id column exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='subscriptions' AND column_name='price_id';
                """))
                
                if result.fetchone():
                    print("⚠️  Found old price_id column. Renaming to stripe_price_id...")
                    conn.execute(text("""
                        ALTER TABLE subscriptions 
                        RENAME COLUMN price_id TO stripe_price_id;
                    """))
                    print("✅ Renamed price_id to stripe_price_id")
                else:
                    print("⚠️  stripe_price_id missing. Adding it...")
                    conn.execute(text("""
                        ALTER TABLE subscriptions 
                        ADD COLUMN stripe_price_id VARCHAR(255);
                    """))
                    print("✅ stripe_price_id column added")
            
            # Step 4: Add indexes if they don't exist
            print("\n[4/4] Adding indexes for performance...")
            
            # Index on billing_period
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_subscriptions_billing_period 
                    ON subscriptions(billing_period);
                """))
                print("✅ Index on billing_period created")
            except Exception as e:
                print(f"⚠️  Index may already exist: {e}")
            
            # Commit transaction
            trans.commit()
            print("\n" + "=" * 60)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"\nSummary:")
            print(f"  - Added/verified billing_period column")
            print(f"  - Renamed price_id to stripe_price_id")
            print(f"  - Updated {updated_count} existing subscription(s)")
            print(f"  - Added performance indexes")
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
        # Check all expected columns exist
        print("\n[1/2] Checking required columns...")
        
        required_columns = {
            'billing_period': 'character varying',
            'stripe_price_id': 'character varying'
        }
        
        all_good = True
        for col_name, expected_type in required_columns.items():
            result = conn.execute(text(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name='subscriptions' AND column_name='{col_name}';
            """))
            row = result.fetchone()
            if row:
                print(f"✅ {col_name}: {row[1]} (nullable={row[2]})")
            else:
                print(f"❌ {col_name}: NOT FOUND")
                all_good = False
        
        # Check subscriptions have billing_period set
        print("\n[2/2] Checking subscriptions data...")
        result = conn.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(billing_period) as with_billing_period,
                   COUNT(*) - COUNT(billing_period) as missing_billing_period
            FROM subscriptions;
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Total subscriptions: {row[0]}")
            print(f"✅ With billing_period: {row[1]}")
            print(f"{'✅' if row[2] == 0 else '⚠️ '} Missing billing_period: {row[2]}")
        
        print("\n" + "=" * 60)
        if all_good:
            print("✅ VERIFICATION COMPLETE - ALL GOOD!")
        else:
            print("⚠️  VERIFICATION FOUND ISSUES")
        print("=" * 60)
        return all_good


if __name__ == "__main__":
    try:
        run_migration()
        verify_migration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

