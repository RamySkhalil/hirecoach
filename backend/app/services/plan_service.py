"""
Plan Service - Manages pricing plans, subscriptions, and feature lookups.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models import (
    PricingPlan, PlanPrice, PlanFeature, Subscription,
    User, SubscriptionStatus
)


class PlanService:
    """Service for managing pricing plans and subscriptions."""
    
    @staticmethod
    def get_plan_by_code(db: Session, code: str) -> Optional[PricingPlan]:
        """
        Get a pricing plan by its code (e.g., 'free', 'pro').
        
        Args:
            db: Database session
            code: Plan code
            
        Returns:
            PricingPlan object or None
        """
        return db.query(PricingPlan).filter_by(code=code, is_active=True).first()
    
    @staticmethod
    def get_plan_by_id(db: Session, plan_id: int) -> Optional[PricingPlan]:
        """
        Get a pricing plan by its ID.
        
        Args:
            db: Database session
            plan_id: Plan ID
            
        Returns:
            PricingPlan object or None
        """
        return db.query(PricingPlan).filter_by(id=plan_id, is_active=True).first()
    
    @staticmethod
    def get_all_active_plans(db: Session) -> List[PricingPlan]:
        """
        Get all active pricing plans, ordered by sort_order.
        
        Args:
            db: Database session
            
        Returns:
            List of PricingPlan objects
        """
        return db.query(PricingPlan).filter_by(is_active=True).order_by(PricingPlan.sort_order).all()
    
    @staticmethod
    def get_user_plan(db: Session, user_id: str) -> PricingPlan:
        """
        Get the current pricing plan for a user.
        If user has no subscription, returns the free plan.
        
        Args:
            db: Database session
            user_id: User ID (Clerk user ID)
            
        Returns:
            PricingPlan object (never None - defaults to free plan)
        """
        # Try to get user's subscription
        subscription = db.query(Subscription).filter_by(
            user_id=user_id,
            status=SubscriptionStatus.ACTIVE
        ).first()
        
        if subscription and subscription.plan:
            return subscription.plan
        
        # Default to free plan
        free_plan = db.query(PricingPlan).filter_by(code='free', is_active=True).first()
        
        if not free_plan:
            raise ValueError("Free plan not found in database. Please seed initial data.")
        
        return free_plan
    
    @staticmethod
    def get_user_subscription(db: Session, user_id: str) -> Optional[Subscription]:
        """
        Get user's active subscription.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Subscription object or None
        """
        return db.query(Subscription).filter_by(
            user_id=user_id,
            status=SubscriptionStatus.ACTIVE
        ).first()
    
    @staticmethod
    def get_plan_feature(
        db: Session,
        plan_id: int,
        feature_code: str
    ) -> Optional[PlanFeature]:
        """
        Get a specific feature configuration for a plan.
        
        Args:
            db: Database session
            plan_id: Plan ID
            feature_code: Feature code (e.g., 'cv_generate')
            
        Returns:
            PlanFeature object or None
        """
        return db.query(PlanFeature).filter_by(
            plan_id=plan_id,
            feature_code=feature_code
        ).first()
    
    @staticmethod
    def get_plan_features(db: Session, plan_id: int) -> List[PlanFeature]:
        """
        Get all features for a plan.
        
        Args:
            db: Database session
            plan_id: Plan ID
            
        Returns:
            List of PlanFeature objects
        """
        return db.query(PlanFeature).filter_by(plan_id=plan_id).all()
    
    @staticmethod
    def create_subscription(
        db: Session,
        user_id: str,
        plan_code: str,
        billing_period: str = "monthly",
        trial_days: int = 0
    ) -> Subscription:
        """
        Create a new subscription for a user.
        
        Args:
            db: Database session
            user_id: User ID
            plan_code: Plan code (e.g., 'pro')
            billing_period: 'monthly' or 'yearly'
            trial_days: Number of trial days
            
        Returns:
            Subscription object
        """
        # Get plan
        plan = PlanService.get_plan_by_code(db, plan_code)
        if not plan:
            raise ValueError(f"Plan with code '{plan_code}' not found")
        
        # Check if user already has a subscription
        existing = db.query(Subscription).filter_by(user_id=user_id).first()
        if existing:
            # Update existing subscription
            existing.plan_id = plan.id
            existing.billing_period = billing_period
            existing.status = SubscriptionStatus.ACTIVE
            existing.current_period_start = datetime.utcnow()
            existing.current_period_end = PlanService._calculate_period_end(billing_period)
            
            if trial_days > 0:
                existing.trial_ends_at = datetime.utcnow() + timedelta(days=trial_days)
            
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new subscription
        now = datetime.utcnow()
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            billing_period=billing_period,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=now,
            current_period_end=PlanService._calculate_period_end(billing_period),
            trial_ends_at=now + timedelta(days=trial_days) if trial_days > 0 else None
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def _calculate_period_end(billing_period: str) -> datetime:
        """Calculate end date for billing period."""
        now = datetime.utcnow()
        if billing_period == "yearly":
            return now + timedelta(days=365)
        else:  # monthly
            return now + timedelta(days=30)
    
    @staticmethod
    def format_plan_for_api(
        db: Session,
        plan: PricingPlan,
        include_features: bool = True
    ) -> Dict[str, Any]:
        """
        Format a plan object for API response.
        
        Args:
            db: Database session
            plan: PricingPlan object
            include_features: Whether to include feature details
            
        Returns:
            Dictionary with plan data
        """
        result = {
            "code": plan.code,
            "name": plan.name,
            "description": plan.description,
            "sort_order": plan.sort_order,
            "prices": []
        }
        
        # Add prices
        for price in plan.prices:
            result["prices"].append({
                "billing_period": price.billing_period,
                "price_cents": price.price_cents,
                "currency": price.currency,
                "trial_days": price.trial_days,
                "display_price": PlanService._format_price(price.price_cents, price.currency)
            })
        
        # Add features if requested
        if include_features:
            result["features"] = []
            for feature in plan.features:
                result["features"].append({
                    "feature_code": feature.feature_code,
                    "monthly_quota": feature.monthly_quota,
                    "hard_cap": feature.hard_cap,
                    "display_quota": PlanService._format_quota(feature.monthly_quota)
                })
        
        return result
    
    @staticmethod
    def _format_price(price_cents: int, currency: str) -> str:
        """Format price for display."""
        if price_cents == 0:
            return "Free"
        
        price_dollars = price_cents / 100.0
        if currency == "USD":
            return f"${price_dollars:.2f}"
        else:
            return f"{price_dollars:.2f} {currency}"
    
    @staticmethod
    def _format_quota(quota: Optional[int]) -> str:
        """Format quota for display."""
        if quota is None:
            return "Unlimited"
        elif quota == 0:
            return "Not available"
        else:
            return str(quota)

