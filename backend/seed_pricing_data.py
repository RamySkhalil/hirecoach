"""
Seed script for initializing pricing plans, features, and model pricing.

Run this script after creating the database tables to populate initial data:
    python seed_pricing_data.py

This will create:
- Pricing plans (Free, Basic, Pro, Enterprise)
- Plan prices (monthly and yearly)
- Feature quotas for each plan
- OpenAI model pricing
"""
import sys
from sqlalchemy.orm import Session

from app.db import SessionLocal, init_db
from app.models import PricingPlan, PlanPrice, PlanFeature, ModelPricing
from app.services.token_usage_service import TokenUsageService


def seed_pricing_plans(db: Session):
    """Create pricing plans."""
    print("\n" + "="*60)
    print("Creating Pricing Plans...")
    print("="*60)
    
    plans = [
        {
            "code": "free",
            "name": "Free",
            "description": "Try the app and get a taste of AI-powered career tools",
            "sort_order": 1
        },
        {
            "code": "basic",
            "name": "Basic",
            "description": "Essential tools for active job seekers",
            "sort_order": 2
        },
        {
            "code": "pro",
            "name": "Pro",
            "description": "Advanced features for serious career advancement",
            "sort_order": 3
        },
        {
            "code": "enterprise",
            "name": "Enterprise",
            "description": "Unlimited access for teams and organizations",
            "sort_order": 4
        }
    ]
    
    created_plans = {}
    for plan_data in plans:
        existing = db.query(PricingPlan).filter_by(code=plan_data["code"]).first()
        if existing:
            print(f"  ⏭️  Plan '{plan_data['name']}' already exists")
            created_plans[plan_data["code"]] = existing
        else:
            plan = PricingPlan(**plan_data)
            db.add(plan)
            db.flush()
            created_plans[plan_data["code"]] = plan
            print(f"  ✅ Created plan: {plan_data['name']}")
    
    db.commit()
    return created_plans


def seed_plan_prices(db: Session, plans: dict):
    """Create prices for each plan."""
    print("\n" + "="*60)
    print("Creating Plan Prices...")
    print("="*60)
    
    prices = [
        # Free plan
        {"plan": "free", "billing_period": "monthly", "price_cents": 0, "trial_days": 0},
        {"plan": "free", "billing_period": "yearly", "price_cents": 0, "trial_days": 0},
        
        # Basic plan - $9.99/month or $99/year (save 17%)
        {"plan": "basic", "billing_period": "monthly", "price_cents": 999, "trial_days": 7},
        {"plan": "basic", "billing_period": "yearly", "price_cents": 9900, "trial_days": 14},
        
        # Pro plan - $29.99/month or $299/year (save 17%)
        {"plan": "pro", "billing_period": "monthly", "price_cents": 2999, "trial_days": 7},
        {"plan": "pro", "billing_period": "yearly", "price_cents": 29900, "trial_days": 14},
        
        # Enterprise plan - $99.99/month or $999/year (save 17%)
        {"plan": "enterprise", "billing_period": "monthly", "price_cents": 9999, "trial_days": 14},
        {"plan": "enterprise", "billing_period": "yearly", "price_cents": 99900, "trial_days": 30},
    ]
    
    for price_data in prices:
        plan_code = price_data.pop("plan")
        plan = plans[plan_code]
        
        existing = db.query(PlanPrice).filter_by(
            plan_id=plan.id,
            billing_period=price_data["billing_period"]
        ).first()
        
        if existing:
            # Update existing price
            existing.price_cents = price_data["price_cents"]
            existing.trial_days = price_data["trial_days"]
            print(f"  🔄 Updated price: {plan.name} - {price_data['billing_period']}")
        else:
            price = PlanPrice(plan_id=plan.id, **price_data)
            db.add(price)
            print(f"  ✅ Created price: {plan.name} - {price_data['billing_period']} = ${price_data['price_cents']/100:.2f}")
    
    db.commit()


def seed_plan_features(db: Session, plans: dict):
    """Create feature quotas for each plan."""
    print("\n" + "="*60)
    print("Creating Plan Features...")
    print("="*60)
    
    features = [
        # Free plan - limited features
        {"plan": "free", "feature_code": "cv_generate", "monthly_quota": 2, "hard_cap": True},
        {"plan": "free", "feature_code": "cv_analyze", "monthly_quota": 2, "hard_cap": True},
        {"plan": "free", "feature_code": "cover_letter_generate", "monthly_quota": 1, "hard_cap": True},
        {"plan": "free", "feature_code": "mock_interview", "monthly_quota": 1, "hard_cap": True},
        {"plan": "free", "feature_code": "career_chat_messages", "monthly_quota": 10, "hard_cap": True},
        
        # Basic plan - good for active job seekers
        {"plan": "basic", "feature_code": "cv_generate", "monthly_quota": 10, "hard_cap": True},
        {"plan": "basic", "feature_code": "cv_analyze", "monthly_quota": 10, "hard_cap": True},
        {"plan": "basic", "feature_code": "cover_letter_generate", "monthly_quota": 20, "hard_cap": True},
        {"plan": "basic", "feature_code": "motivation_letter_generate", "monthly_quota": 10, "hard_cap": True},
        {"plan": "basic", "feature_code": "mock_interview", "monthly_quota": 5, "hard_cap": True},
        {"plan": "basic", "feature_code": "career_chat_messages", "monthly_quota": 100, "hard_cap": True},
        {"plan": "basic", "feature_code": "job_tracking", "monthly_quota": 50, "hard_cap": False},
        
        # Pro plan - serious job seekers
        {"plan": "pro", "feature_code": "cv_generate", "monthly_quota": 30, "hard_cap": True},
        {"plan": "pro", "feature_code": "cv_analyze", "monthly_quota": 30, "hard_cap": True},
        {"plan": "pro", "feature_code": "cover_letter_generate", "monthly_quota": None, "hard_cap": False},  # Unlimited
        {"plan": "pro", "feature_code": "motivation_letter_generate", "monthly_quota": None, "hard_cap": False},
        {"plan": "pro", "feature_code": "mock_interview", "monthly_quota": 20, "hard_cap": True},
        {"plan": "pro", "feature_code": "career_chat_messages", "monthly_quota": None, "hard_cap": False},  # Unlimited
        {"plan": "pro", "feature_code": "job_tracking", "monthly_quota": None, "hard_cap": False},
        
        # Enterprise plan - unlimited everything
        {"plan": "enterprise", "feature_code": "cv_generate", "monthly_quota": None, "hard_cap": False},
        {"plan": "enterprise", "feature_code": "cv_analyze", "monthly_quota": None, "hard_cap": False},
        {"plan": "enterprise", "feature_code": "cover_letter_generate", "monthly_quota": None, "hard_cap": False},
        {"plan": "enterprise", "feature_code": "motivation_letter_generate", "monthly_quota": None, "hard_cap": False},
        {"plan": "enterprise", "feature_code": "mock_interview", "monthly_quota": None, "hard_cap": False},
        {"plan": "enterprise", "feature_code": "career_chat_messages", "monthly_quota": None, "hard_cap": False},
        {"plan": "enterprise", "feature_code": "job_tracking", "monthly_quota": None, "hard_cap": False},
    ]
    
    for feature_data in features:
        plan_code = feature_data.pop("plan")
        plan = plans[plan_code]
        
        existing = db.query(PlanFeature).filter_by(
            plan_id=plan.id,
            feature_code=feature_data["feature_code"]
        ).first()
        
        quota_display = "Unlimited" if feature_data["monthly_quota"] is None else str(feature_data["monthly_quota"])
        
        if existing:
            # Update existing feature
            existing.monthly_quota = feature_data["monthly_quota"]
            existing.hard_cap = feature_data["hard_cap"]
            print(f"  🔄 Updated: {plan.name} - {feature_data['feature_code']}: {quota_display}")
        else:
            feature = PlanFeature(plan_id=plan.id, **feature_data)
            db.add(feature)
            print(f"  ✅ Created: {plan.name} - {feature_data['feature_code']}: {quota_display}")
    
    db.commit()


def seed_model_pricing(db: Session):
    """Create OpenAI model pricing."""
    print("\n" + "="*60)
    print("Creating Model Pricing...")
    print("="*60)
    
    TokenUsageService.seed_model_pricing(db)


def main():
    """Main seeding function."""
    print("\n" + "🌱 "*20)
    print("PRICING DATA SEED SCRIPT")
    print("🌱 "*20)
    
    try:
        # Initialize database (create tables if they don't exist)
        print("\nInitializing database...")
        init_db()
        print("✅ Database initialized")
        
        # Create session
        db = SessionLocal()
        
        try:
            # Seed data
            plans = seed_pricing_plans(db)
            seed_plan_prices(db, plans)
            seed_plan_features(db, plans)
            seed_model_pricing(db)
            
            print("\n" + "="*60)
            print("✅ SEED COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("\nYou can now:")
            print("  1. Start the backend: uvicorn app.main:app --reload")
            print("  2. Test pricing endpoint: GET /pricing/plans")
            print("  3. View admin stats: GET /admin/health/database")
            print("\n")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

