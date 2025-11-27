"""
Admin routes - Internal analytics and management endpoints.
WARNING: These endpoints should be protected with admin authentication in production!
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.db import get_db
from app.services.token_usage_service import TokenUsageService
from app.services.quota_service import QuotaService
from app.services.plan_service import PlanService

router = APIRouter(prefix="/admin", tags=["Admin"])


# TODO: Add admin authentication middleware
# For now, these endpoints are unprotected - ADD AUTH BEFORE PRODUCTION!


@router.get("/stats/revenue-vs-cost")
def get_revenue_vs_cost(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get revenue vs cost analysis.
    
    Shows:
    - Total LLM API costs (OpenAI token usage)
    - Total revenue (placeholder for now - integrate with Stripe/Paymob)
    - Estimated profit/loss
    - Breakdown by model and feature
    
    WARNING: This endpoint should require admin authentication in production!
    
    Args:
        days: Number of days to analyze (default: 30)
        
    Returns:
        Revenue vs cost analysis
    """
    try:
        # Get cost summary
        cost_summary = TokenUsageService.get_total_cost_summary(db, days)
        
        # TODO: Get actual revenue from payment provider
        # For now, use placeholder revenue calculation
        # In production: integrate with Stripe/Paymob webhooks
        total_revenue_usd = 0.0  # Placeholder
        
        # Calculate profit
        total_cost_usd = cost_summary["total_cost_usd"]
        estimated_profit_usd = total_revenue_usd - total_cost_usd
        
        # Calculate margins
        profit_margin = (
            (estimated_profit_usd / total_revenue_usd * 100)
            if total_revenue_usd > 0
            else 0.0
        )
        
        return {
            "period_days": days,
            "period_start": cost_summary["period_start"],
            "period_end": cost_summary["period_end"],
            
            # Financial metrics
            "total_revenue_usd": round(total_revenue_usd, 2),
            "total_llm_cost_usd": round(total_cost_usd, 2),
            "estimated_profit_usd": round(estimated_profit_usd, 2),
            "profit_margin_percent": round(profit_margin, 2),
            
            # Usage metrics
            "total_requests": cost_summary["total_requests"],
            "unique_users": cost_summary["unique_users"],
            "total_tokens": cost_summary["total_tokens"],
            "avg_cost_per_request": cost_summary["avg_cost_per_request"],
            "avg_cost_per_user": (
                round(total_cost_usd / cost_summary["unique_users"], 4)
                if cost_summary["unique_users"] > 0
                else 0
            ),
            
            # Breakdowns
            "by_model": cost_summary["by_model"],
            "by_feature": cost_summary["by_feature"],
            "daily_breakdown": cost_summary["daily"],
            
            # Warnings
            "warnings": [
                "Revenue integration pending - connect Stripe/Paymob webhooks",
                "Add admin authentication before deploying to production",
                f"Current burn rate: ${round(total_cost_usd / days, 2)}/day"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate cost analysis: {str(e)}"
        )


@router.get("/stats/user-costs/{user_id}")
def get_user_cost_analysis(
    user_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get cost analysis for a specific user.
    
    Shows how much a specific user is costing in LLM API calls.
    Useful for identifying high-usage users or potential abuse.
    
    WARNING: This endpoint should require admin authentication in production!
    
    Args:
        user_id: User ID to analyze
        days: Number of days to analyze
        
    Returns:
        User cost analysis
    """
    try:
        cost_summary = TokenUsageService.get_user_cost_summary(db, user_id, days)
        
        # Get user's plan
        try:
            plan = PlanService.get_user_plan(db, user_id)
            plan_info = {
                "plan_code": plan.code,
                "plan_name": plan.name
            }
        except Exception:
            plan_info = {
                "plan_code": "unknown",
                "plan_name": "Unknown"
            }
        
        return {
            **cost_summary,
            "plan": plan_info,
            "avg_cost_per_day": round(cost_summary["total_cost_usd"] / days, 4)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user cost analysis: {str(e)}"
        )


@router.get("/stats/plans")
def get_plan_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get statistics about plan distribution and usage.
    
    Shows:
    - Number of users on each plan
    - Feature usage by plan
    - Plan distribution
    
    WARNING: This endpoint should require admin authentication in production!
    """
    try:
        from app.models import Subscription, SubscriptionStatus
        from sqlalchemy import func
        
        # Get subscription distribution
        subscription_counts = db.query(
            Subscription.plan_id,
            func.count(Subscription.id).label('count')
        ).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).group_by(Subscription.plan_id).all()
        
        # Get plan details
        plans = PlanService.get_all_active_plans(db)
        plan_stats = []
        
        for plan in plans:
            # Count subscriptions for this plan
            count = next(
                (row.count for row in subscription_counts if row.plan_id == plan.id),
                0
            )
            
            plan_stats.append({
                "plan_code": plan.code,
                "plan_name": plan.name,
                "active_subscriptions": count,
                "features_count": len(plan.features)
            })
        
        # Total active subscriptions
        total_subscriptions = sum(stat["active_subscriptions"] for stat in plan_stats)
        
        # Calculate percentages
        for stat in plan_stats:
            stat["percentage"] = (
                round(stat["active_subscriptions"] / total_subscriptions * 100, 2)
                if total_subscriptions > 0
                else 0
            )
        
        return {
            "total_active_subscriptions": total_subscriptions,
            "plans": sorted(plan_stats, key=lambda x: x["active_subscriptions"], reverse=True)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get plan statistics: {str(e)}"
        )


@router.get("/stats/features")
def get_feature_usage_stats(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get feature usage statistics across all users.
    
    Shows which features are most popular and their associated costs.
    
    WARNING: This endpoint should require admin authentication in production!
    """
    try:
        from app.models import UserFeatureUsage, TokenUsageLog
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get feature usage counts
        feature_usage = db.query(
            UserFeatureUsage.feature_code,
            func.sum(UserFeatureUsage.used_count).label('total_uses'),
            func.count(func.distinct(UserFeatureUsage.user_id)).label('unique_users')
        ).filter(
            UserFeatureUsage.period_end >= start_date
        ).group_by(UserFeatureUsage.feature_code).all()
        
        # Get feature costs
        feature_costs = db.query(
            TokenUsageLog.feature_code,
            func.sum(TokenUsageLog.cost_usd).label('total_cost')
        ).filter(
            TokenUsageLog.created_at >= start_date,
            TokenUsageLog.feature_code.isnot(None)
        ).group_by(TokenUsageLog.feature_code).all()
        
        # Combine data
        features = {}
        for usage in feature_usage:
            features[usage.feature_code] = {
                "feature_code": usage.feature_code,
                "total_uses": usage.total_uses,
                "unique_users": usage.unique_users,
                "total_cost_usd": 0.0
            }
        
        for cost in feature_costs:
            if cost.feature_code in features:
                features[cost.feature_code]["total_cost_usd"] = round(cost.total_cost, 4)
            else:
                features[cost.feature_code] = {
                    "feature_code": cost.feature_code,
                    "total_uses": 0,
                    "unique_users": 0,
                    "total_cost_usd": round(cost.total_cost, 4)
                }
        
        # Calculate avg cost per use
        for feature in features.values():
            if feature["total_uses"] > 0:
                feature["avg_cost_per_use"] = round(
                    feature["total_cost_usd"] / feature["total_uses"],
                    6
                )
            else:
                feature["avg_cost_per_use"] = 0.0
        
        return {
            "period_days": days,
            "features": sorted(
                list(features.values()),
                key=lambda x: x["total_uses"],
                reverse=True
            )
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feature usage stats: {str(e)}"
        )


@router.get("/health/database")
def check_database_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Check database health and table status.
    
    Returns counts of records in key tables.
    """
    try:
        from app.models import (
            PricingPlan, PlanPrice, PlanFeature, Subscription,
            UserFeatureUsage, ModelPricing, TokenUsageLog
        )
        
        return {
            "status": "healthy",
            "tables": {
                "pricing_plans": db.query(PricingPlan).count(),
                "plan_prices": db.query(PlanPrice).count(),
                "plan_features": db.query(PlanFeature).count(),
                "subscriptions": db.query(Subscription).count(),
                "user_feature_usage": db.query(UserFeatureUsage).count(),
                "model_pricing": db.query(ModelPricing).count(),
                "token_usage_log": db.query(TokenUsageLog).count()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )

