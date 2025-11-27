"""
Pricing System Seed Script

This script populates the pricing tables with initial data:
- pricing_plans (Free, Basic, Pro)
- plan_prices (monthly and yearly for each plan)
- plan_features (feature quotas per plan)
- model_pricing (OpenAI model costs)

The script is IDEMPOTENT - safe to run multiple times.
It will not create duplicate records.

Usage:
    cd backend
    python -m app.seed_pricing
    # or
    python app/seed_pricing.py

Requirements:
    - Database tables must already exist (run migrations first)
    - DATABASE_URL must be configured in .env
"""

from sqlalchemy.orm import Session
from app.db import SessionLocal, init_db
from app.models import PricingPlan, PlanPrice, PlanFeature, ModelPricing


def seed_pricing_plans(db: Session) -> dict:
    """
    Seed the pricing_plans table with Free, Basic, and Pro plans.
    
    Returns:
        Dict mapping plan codes to plan objects
    """
    print("\n" + "="*60)
    print("SEEDING PRICING PLANS")
    print("="*60)
    
    plans_data = [
        {
            "code": "free",
            "name": "Free",
            "description": "Get started with limited access",
            "is_active": True,
            "sort_order": 1
        },
        {
            "code": "basic",
            "name": "Basic",
            "description": "For active job seekers",
            "is_active": True,
            "sort_order": 2
        },
        {
            "code": "pro",
            "name": "Pro",
            "description": "For power users and frequent applicants",
            "is_active": True,
            "sort_order": 3
        }
    ]
    
    created_plans = {}
    
    for plan_data in plans_data:
        # Check if plan already exists
        existing_plan = db.query(PricingPlan).filter_by(code=plan_data["code"]).first()
        
        if existing_plan:
            print(f"  ⏭️  Plan '{plan_data['name']}' already exists (ID: {existing_plan.id})")
            created_plans[plan_data["code"]] = existing_plan
        else:
            # Create new plan
            new_plan = PricingPlan(**plan_data)
            db.add(new_plan)
            db.commit()
            db.refresh(new_plan)
            print(f"  ✅ Created plan '{plan_data['name']}' (ID: {new_plan.id})")
            created_plans[plan_data["code"]] = new_plan
    
    print(f"\n✅ Pricing plans seeded: {len(created_plans)} plans")
    return created_plans


def seed_plan_prices(db: Session, plans: dict) -> None:
    """
    Seed the plan_prices table with monthly and yearly prices for each plan.
    
    Args:
        plans: Dict mapping plan codes to plan objects
    """
    print("\n" + "="*60)
    print("SEEDING PLAN PRICES")
    print("="*60)
    
    prices_data = [
        # Free plan
        {"plan_code": "free", "billing_period": "monthly", "price_cents": 0},
        {"plan_code": "free", "billing_period": "yearly", "price_cents": 0},
        
        # Basic plan
        {"plan_code": "basic", "billing_period": "monthly", "price_cents": 499},   # $4.99
        {"plan_code": "basic", "billing_period": "yearly", "price_cents": 4990},   # $49.90
        
        # Pro plan
        {"plan_code": "pro", "billing_period": "monthly", "price_cents": 999},     # $9.99
        {"plan_code": "pro", "billing_period": "yearly", "price_cents": 9990},     # $99.90
    ]
    
    created_count = 0
    skipped_count = 0
    
    for price_data in prices_data:
        plan_code = price_data["plan_code"]
        plan = plans[plan_code]
        
        # Check if price already exists
        existing_price = db.query(PlanPrice).filter_by(
            plan_id=plan.id,
            billing_period=price_data["billing_period"]
        ).first()
        
        if existing_price:
            print(f"  ⏭️  Price for {plan.name} ({price_data['billing_period']}) already exists")
            skipped_count += 1
        else:
            # Create new price
            new_price = PlanPrice(
                plan_id=plan.id,
                billing_period=price_data["billing_period"],
                price_cents=price_data["price_cents"],
                currency="USD",
                trial_days=0
            )
            db.add(new_price)
            db.commit()
            
            price_display = f"${price_data['price_cents'] / 100:.2f}" if price_data['price_cents'] > 0 else "Free"
            print(f"  ✅ Created price: {plan.name} {price_data['billing_period']} = {price_display}")
            created_count += 1
    
    print(f"\n✅ Plan prices seeded: {created_count} created, {skipped_count} already existed")


def seed_plan_features(db: Session, plans: dict) -> None:
    """
    Seed the plan_features table with feature quotas for each plan.
    
    Args:
        plans: Dict mapping plan codes to plan objects
    """
    print("\n" + "="*60)
    print("SEEDING PLAN FEATURES")
    print("="*60)
    
    features_data = [
        # Free plan features
        {
            "plan_code": "free",
            "feature_code": "cv_generate",
            "monthly_quota": 2,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "free",
            "feature_code": "cover_letter_generate",
            "monthly_quota": 2,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "free",
            "feature_code": "motivation_letter_generate",
            "monthly_quota": 2,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "free",
            "feature_code": "mock_interview",
            "monthly_quota": 1,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "free",
            "feature_code": "career_chat_messages",
            "monthly_quota": 50,
            "hard_cap": True,
            "rollover": False
        },
        
        # Basic plan features
        {
            "plan_code": "basic",
            "feature_code": "cv_generate",
            "monthly_quota": 5,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "basic",
            "feature_code": "cover_letter_generate",
            "monthly_quota": 10,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "basic",
            "feature_code": "motivation_letter_generate",
            "monthly_quota": 10,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "basic",
            "feature_code": "mock_interview",
            "monthly_quota": 3,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "basic",
            "feature_code": "career_chat_messages",
            "monthly_quota": 200,
            "hard_cap": True,
            "rollover": False
        },
        
        # Pro plan features
        {
            "plan_code": "pro",
            "feature_code": "cv_generate",
            "monthly_quota": 20,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "pro",
            "feature_code": "cover_letter_generate",
            "monthly_quota": 50,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "pro",
            "feature_code": "motivation_letter_generate",
            "monthly_quota": 50,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "pro",
            "feature_code": "mock_interview",
            "monthly_quota": 10,
            "hard_cap": True,
            "rollover": False
        },
        {
            "plan_code": "pro",
            "feature_code": "career_chat_messages",
            "monthly_quota": 1000,
            "hard_cap": True,
            "rollover": False
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for feature_data in features_data:
        plan_code = feature_data.pop("plan_code")
        plan = plans[plan_code]
        
        # Check if feature already exists
        existing_feature = db.query(PlanFeature).filter_by(
            plan_id=plan.id,
            feature_code=feature_data["feature_code"]
        ).first()
        
        if existing_feature:
            print(f"  ⏭️  Feature {feature_data['feature_code']} for {plan.name} already exists")
            skipped_count += 1
        else:
            # Create new feature
            new_feature = PlanFeature(
                plan_id=plan.id,
                **feature_data
            )
            db.add(new_feature)
            db.commit()
            
            quota_display = f"{feature_data['monthly_quota']}/month"
            print(f"  ✅ Created: {plan.name} - {feature_data['feature_code']}: {quota_display}")
            created_count += 1
    
    print(f"\n✅ Plan features seeded: {created_count} created, {skipped_count} already existed")


def seed_model_pricing(db: Session) -> None:
    """
    Seed the model_pricing table with OpenAI model costs.
    """
    print("\n" + "="*60)
    print("SEEDING MODEL PRICING")
    print("="*60)
    
    models_data = [
        {
            "model_name": "gpt-4.1-mini",
            "input_cost_per_1k": 0.150000,
            "output_cost_per_1k": 0.600000,
            "currency": "USD"
        },
        {
            "model_name": "gpt-4.1",
            "input_cost_per_1k": 5.000000,
            "output_cost_per_1k": 15.000000,
            "currency": "USD"
        },
        {
            "model_name": "gpt-4o-mini",
            "input_cost_per_1k": 0.150000,
            "output_cost_per_1k": 0.600000,
            "currency": "USD"
        },
        {
            "model_name": "gpt-4o",
            "input_cost_per_1k": 2.500000,
            "output_cost_per_1k": 10.000000,
            "currency": "USD"
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for model_data in models_data:
        # Check if model already exists
        existing_model = db.query(ModelPricing).filter_by(
            model_name=model_data["model_name"]
        ).first()
        
        if existing_model:
            print(f"  ⏭️  Model '{model_data['model_name']}' pricing already exists")
            skipped_count += 1
        else:
            # Create new model pricing
            new_model = ModelPricing(**model_data)
            db.add(new_model)
            db.commit()
            
            print(f"  ✅ Created: {model_data['model_name']} "
                  f"(input: ${model_data['input_cost_per_1k']}/1k, "
                  f"output: ${model_data['output_cost_per_1k']}/1k)")
            created_count += 1
    
    print(f"\n✅ Model pricing seeded: {created_count} created, {skipped_count} already existed")


def main():
    """
    Main function to run all seeding operations.
    """
    print("\n" + "🌱 "*30)
    print("PRICING SYSTEM SEED SCRIPT")
    print("🌱 "*30)
    print("\nThis script will populate the following tables:")
    print("  - pricing_plans")
    print("  - plan_prices")
    print("  - plan_features")
    print("  - model_pricing")
    print("\nThe script is IDEMPOTENT - safe to run multiple times.")
    print("It will NOT create duplicate records.\n")
    
    # Initialize database (ensure tables exist)
    print("Initializing database...")
    try:
        init_db()
        print("✅ Database initialized\n")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Seed pricing plans
        plans = seed_pricing_plans(db)
        
        # Step 2: Seed plan prices
        seed_plan_prices(db, plans)
        
        # Step 3: Seed plan features
        seed_plan_features(db, plans)
        
        # Step 4: Seed model pricing
        seed_model_pricing(db)
        
        print("\n" + "="*60)
        print("🎉 SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nSummary:")
        print(f"  ✅ {len(plans)} pricing plans")
        print(f"  ✅ {len(plans) * 2} plan prices (monthly + yearly)")
        print(f"  ✅ {len(plans) * 5} plan features (5 features per plan)")
        print(f"  ✅ 4 model pricing entries")
        print("\nYou can now:")
        print("  1. Start the backend: uvicorn app.main:app --reload")
        print("  2. Test the API: GET /pricing/plans")
        print("  3. View plans in database UI")
        print("\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR DURING SEEDING")
        print("="*60)
        print(f"\n{str(e)}\n")
        import traceback
        traceback.print_exc()
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()

