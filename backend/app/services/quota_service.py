"""
Quota Service - Manages feature usage tracking and quota enforcement.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models import UserFeatureUsage, PlanFeature, Subscription
from app.services.plan_service import PlanService


class QuotaExceededError(Exception):
    """Raised when user exceeds their feature quota."""
    
    def __init__(self, feature_code: str, limit: int, used: int):
        self.feature_code = feature_code
        self.limit = limit
        self.used = used
        super().__init__(
            f"Quota exceeded for feature '{feature_code}'. "
            f"Used {used}/{limit} for current period."
        )


class QuotaService:
    """Service for managing feature usage quotas."""
    
    @staticmethod
    def check_and_increment_usage(
        db: Session,
        user_id: str,
        feature_code: str
    ) -> bool:
        """
        Check if user can use a feature and increment usage counter.
        
        Args:
            db: Database session
            user_id: User ID
            feature_code: Feature code (e.g., 'cv_generate')
            
        Returns:
            True if usage allowed and incremented
            
        Raises:
            QuotaExceededError: If user has exceeded their quota
        """
        # Get user's current plan
        plan = PlanService.get_user_plan(db, user_id)
        
        # Get feature configuration for this plan
        feature = PlanService.get_plan_feature(db, plan.id, feature_code)
        
        # If feature not configured for this plan, check if it's unlimited
        if not feature:
            # Feature not explicitly configured - allow by default
            # (For features that don't have quotas)
            return True
        
        # Check if feature is unlimited (quota = None)
        if feature.monthly_quota is None:
            return True
        
        # Check if feature is disabled (quota = 0)
        if feature.monthly_quota == 0:
            raise QuotaExceededError(
                feature_code=feature_code,
                limit=0,
                used=0
            )
        
        # Get current billing period
        subscription = PlanService.get_user_subscription(db, user_id)
        if subscription:
            period_start = subscription.current_period_start
            period_end = subscription.current_period_end
        else:
            # No subscription - use monthly period from now
            from datetime import timedelta
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = (period_start + timedelta(days=32)).replace(day=1)
        
        # Get or create usage record
        usage = db.query(UserFeatureUsage).filter(
            and_(
                UserFeatureUsage.user_id == user_id,
                UserFeatureUsage.plan_id == plan.id,
                UserFeatureUsage.feature_code == feature_code,
                UserFeatureUsage.period_start == period_start,
                UserFeatureUsage.period_end == period_end
            )
        ).first()
        
        if not usage:
            # Create new usage record
            usage = UserFeatureUsage(
                user_id=user_id,
                plan_id=plan.id,
                feature_code=feature_code,
                period_start=period_start,
                period_end=period_end,
                used_count=0
            )
            db.add(usage)
            db.flush()
        
        # Check if quota exceeded
        if usage.used_count >= feature.monthly_quota:
            if feature.hard_cap:
                raise QuotaExceededError(
                    feature_code=feature_code,
                    limit=feature.monthly_quota,
                    used=usage.used_count
                )
            else:
                # Soft cap - allow but log warning
                print(f"⚠️  User {user_id} exceeded soft cap for {feature_code}")
        
        # Increment usage
        usage.used_count += 1
        usage.updated_at = datetime.utcnow()
        db.commit()
        
        return True
    
    @staticmethod
    def get_usage_stats(
        db: Session,
        user_id: str,
        feature_code: Optional[str] = None
    ) -> dict:
        """
        Get usage statistics for a user.
        
        Args:
            db: Database session
            user_id: User ID
            feature_code: Optional feature code to filter by
            
        Returns:
            Dictionary with usage stats
        """
        # Get user's plan
        plan = PlanService.get_user_plan(db, user_id)
        subscription = PlanService.get_user_subscription(db, user_id)
        
        # Get billing period
        if subscription:
            period_start = subscription.current_period_start
            period_end = subscription.current_period_end
        else:
            from datetime import timedelta
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = (period_start + timedelta(days=32)).replace(day=1)
        
        # Build query
        query = db.query(UserFeatureUsage).filter(
            and_(
                UserFeatureUsage.user_id == user_id,
                UserFeatureUsage.period_start == period_start,
                UserFeatureUsage.period_end == period_end
            )
        )
        
        if feature_code:
            query = query.filter(UserFeatureUsage.feature_code == feature_code)
        
        usages = query.all()
        
        # Build response
        stats = {
            "plan_code": plan.code,
            "plan_name": plan.name,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "features": {}
        }
        
        # Get all features for this plan
        all_features = PlanService.get_plan_features(db, plan.id)
        
        for feature in all_features:
            # Find usage for this feature
            usage = next(
                (u for u in usages if u.feature_code == feature.feature_code),
                None
            )
            
            stats["features"][feature.feature_code] = {
                "used": usage.used_count if usage else 0,
                "limit": feature.monthly_quota,
                "remaining": (
                    feature.monthly_quota - (usage.used_count if usage else 0)
                    if feature.monthly_quota is not None
                    else None
                ),
                "unlimited": feature.monthly_quota is None,
                "percentage_used": (
                    (usage.used_count / feature.monthly_quota * 100)
                    if feature.monthly_quota and feature.monthly_quota > 0
                    else 0
                ) if usage else 0
            }
        
        return stats
    
    @staticmethod
    def reset_usage_for_period(
        db: Session,
        user_id: str
    ) -> None:
        """
        Reset usage counters for a new billing period.
        
        This should be called when a subscription renews.
        
        Args:
            db: Database session
            user_id: User ID
        """
        # Get current subscription
        subscription = PlanService.get_user_subscription(db, user_id)
        if not subscription:
            return
        
        # Delete old usage records (or mark as archived)
        db.query(UserFeatureUsage).filter(
            and_(
                UserFeatureUsage.user_id == user_id,
                UserFeatureUsage.period_end < datetime.utcnow()
            )
        ).delete()
        
        db.commit()
    
    @staticmethod
    def can_use_feature(
        db: Session,
        user_id: str,
        feature_code: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if user can use a feature without incrementing counter.
        
        Args:
            db: Database session
            user_id: User ID
            feature_code: Feature code
            
        Returns:
            Tuple of (can_use: bool, reason: Optional[str])
        """
        try:
            # Get user's plan
            plan = PlanService.get_user_plan(db, user_id)
            
            # Get feature configuration
            feature = PlanService.get_plan_feature(db, plan.id, feature_code)
            
            # Feature not configured - allow
            if not feature:
                return True, None
            
            # Unlimited quota
            if feature.monthly_quota is None:
                return True, None
            
            # Feature disabled
            if feature.monthly_quota == 0:
                return False, f"Feature '{feature_code}' is not available on your plan"
            
            # Get current usage
            subscription = PlanService.get_user_subscription(db, user_id)
            if subscription:
                period_start = subscription.current_period_start
                period_end = subscription.current_period_end
            else:
                from datetime import timedelta
                period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                period_end = (period_start + timedelta(days=32)).replace(day=1)
            
            usage = db.query(UserFeatureUsage).filter(
                and_(
                    UserFeatureUsage.user_id == user_id,
                    UserFeatureUsage.plan_id == plan.id,
                    UserFeatureUsage.feature_code == feature_code,
                    UserFeatureUsage.period_start == period_start,
                    UserFeatureUsage.period_end == period_end
                )
            ).first()
            
            used = usage.used_count if usage else 0
            
            if used >= feature.monthly_quota:
                if feature.hard_cap:
                    return False, f"You've used {used}/{feature.monthly_quota} for this month. Upgrade to continue."
                else:
                    return True, None  # Soft cap
            
            return True, None
            
        except Exception as e:
            print(f"Error checking feature access: {e}")
            return False, "Error checking feature access"

