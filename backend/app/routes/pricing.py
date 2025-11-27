"""
Pricing routes - Public endpoints for pricing plans and features.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.db import get_db
from app.models import PlanPrice
from app.services.plan_service import PlanService
from app.services.quota_service import QuotaService

router = APIRouter(prefix="/pricing", tags=["Pricing"])


class SubscribeToPlanRequest(BaseModel):
    """Request body for subscribing to a plan."""
    user_id: str
    plan_code: str
    billing_period: str = "monthly"  # 'monthly' or 'yearly'


@router.get("/plans")
def get_pricing_plans(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get all active pricing plans with their prices and features.
    
    Returns a list of plans formatted for display in the pricing page.
    Each plan includes:
    - Basic info (code, name, description)
    - Prices for monthly and yearly billing
    - Feature quotas and limits
    
    This endpoint is public and doesn't require authentication.
    """
    try:
        # Get all active plans
        plans = PlanService.get_all_active_plans(db)
        
        # Format for API response
        result = []
        for plan in plans:
            formatted_plan = PlanService.format_plan_for_api(db, plan, include_features=True)
            result.append(formatted_plan)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve pricing plans: {str(e)}"
        )


@router.get("/plans/{plan_code}")
def get_plan_details(
    plan_code: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific plan.
    
    Args:
        plan_code: Plan code (e.g., 'free', 'pro')
        
    Returns:
        Plan details with prices and features
    """
    plan = PlanService.get_plan_by_code(db, plan_code)
    
    if not plan:
        raise HTTPException(
            status_code=404,
            detail=f"Plan with code '{plan_code}' not found"
        )
    
    return PlanService.format_plan_for_api(db, plan, include_features=True)


@router.get("/features")
def get_all_features(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get a list of all features with descriptions.
    
    Returns a mapping of feature codes to human-readable descriptions.
    Useful for displaying feature names in the UI.
    """
    # Define feature descriptions
    # In a real app, these might come from a database table
    features = {
        "cv_generate": {
            "name": "CV Generation",
            "description": "Generate professional CVs with AI assistance",
            "icon": "file-text"
        },
        "cv_analyze": {
            "name": "CV Analysis",
            "description": "Get detailed analysis and ATS scores for your CV",
            "icon": "search"
        },
        "cover_letter_generate": {
            "name": "Cover Letter Generation",
            "description": "Create tailored cover letters for job applications",
            "icon": "mail"
        },
        "motivation_letter_generate": {
            "name": "Motivation Letter",
            "description": "Write compelling motivation letters",
            "icon": "edit"
        },
        "mock_interview": {
            "name": "Mock Interviews",
            "description": "Practice with AI-powered interview simulations",
            "icon": "mic"
        },
        "career_chat_messages": {
            "name": "Career Coaching Chat",
            "description": "Get unlimited career advice from AI coach",
            "icon": "message-circle"
        },
        "job_tracking": {
            "name": "Job Application Tracking",
            "description": "Track your job applications in one place",
            "icon": "briefcase"
        }
    }
    
    return {
        "features": features
    }


@router.get("/compare")
def compare_plans(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get a comparison view of all plans.
    
    Returns plans organized in a format optimized for comparison tables.
    Each feature shows which plans include it and their respective quotas.
    """
    try:
        # Get all active plans
        plans = PlanService.get_all_active_plans(db)
        
        # Build comparison structure
        comparison = {
            "plans": [],
            "features": {}
        }
        
        # Get all unique feature codes
        all_feature_codes = set()
        for plan in plans:
            for feature in plan.features:
                all_feature_codes.add(feature.feature_code)
        
        # Build feature comparison
        for feature_code in sorted(all_feature_codes):
            comparison["features"][feature_code] = {
                "feature_code": feature_code,
                "by_plan": {}
            }
            
            for plan in plans:
                feature = PlanService.get_plan_feature(db, plan.id, feature_code)
                if feature:
                    comparison["features"][feature_code]["by_plan"][plan.code] = {
                        "quota": feature.monthly_quota,
                        "unlimited": feature.monthly_quota is None,
                        "available": feature.monthly_quota != 0,
                        "display": PlanService._format_quota(feature.monthly_quota)
                    }
                else:
                    comparison["features"][feature_code]["by_plan"][plan.code] = {
                        "quota": 0,
                        "unlimited": False,
                        "available": False,
                        "display": "Not available"
                    }
        
        # Add plan info
        for plan in plans:
            comparison["plans"].append({
                "code": plan.code,
                "name": plan.name,
                "description": plan.description,
                "sort_order": plan.sort_order
            })
        
        return comparison
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare plans: {str(e)}"
        )


@router.get("/user/usage")
def get_user_usage(
    user_id: str,  # In real app, get from auth token
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get usage statistics for the current user.
    
    Shows how much of each feature quota has been used in the current billing period.
    
    Note: In production, user_id should come from authentication token,
    not as a query parameter.
    """
    try:
        stats = QuotaService.get_usage_stats(db, user_id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve usage stats: {str(e)}"
        )


@router.get("/user/current-plan")
def get_user_current_plan(
    user_id: str,  # TODO: Get from auth token
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the current user's plan information.
    
    Returns:
        - plan_code: Plan code (free, basic, pro)
        - plan_name: Display name
        - billing_period: monthly or yearly
        - price_cents: Current price
        - status: Subscription status
        - current_period_end: When the current period ends
    
    Note: In production, user_id should come from authentication token.
    """
    try:
        # Get user's plan
        plan = PlanService.get_user_plan(db, user_id)
        
        # Get subscription details if exists
        subscription = PlanService.get_user_subscription(db, user_id)
        
        result = {
            "plan_code": plan.code,
            "plan_name": plan.name,
            "plan_description": plan.description
        }
        
        if subscription:
            result.update({
                "billing_period": subscription.billing_period,
                "status": subscription.status.value,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                "is_trial": subscription.trial_ends_at is not None and subscription.trial_ends_at > datetime.utcnow() if subscription.trial_ends_at else False
            })
            
            # Get price for current billing period
            price = db.query(PlanPrice).filter_by(
                plan_id=plan.id,
                billing_period=subscription.billing_period
            ).first()
            
            if price:
                result["price_cents"] = price.price_cents
                result["currency"] = price.currency
        else:
            # No subscription, show monthly price for free plan
            result.update({
                "billing_period": "monthly",
                "status": "active",
                "price_cents": 0,
                "currency": "USD",
                "is_trial": False
            })
        
        return result
        
    except Exception as e:
        # If user not found or no subscription, return free plan
        free_plan = PlanService.get_plan_by_code(db, "free")
        if free_plan:
            return {
                "plan_code": "free",
                "plan_name": "Free",
                "plan_description": "Get started with limited access",
                "billing_period": "monthly",
                "status": "active",
                "price_cents": 0,
                "currency": "USD",
                "is_trial": False
            }
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user plan: {str(e)}"
        )


@router.post("/user/subscribe")
def subscribe_to_plan(
    request: SubscribeToPlanRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Subscribe a user to a pricing plan.
    
    This endpoint creates or updates a user's subscription to a specific plan.
    For now, this is a simple plan assignment without payment integration.
    
    In production, you would:
    1. Verify payment (Stripe/Paymob)
    2. Create subscription in payment provider
    3. Store subscription details
    4. Send confirmation email
    
    Args:
        request: Contains user_id, plan_code, and billing_period
        
    Returns:
        Subscription details and success message
    """
    try:
        # Validate plan exists
        plan = PlanService.get_plan_by_code(db, request.plan_code)
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"Plan with code '{request.plan_code}' not found"
            )
        
        # Validate billing period
        if request.billing_period not in ["monthly", "yearly"]:
            raise HTTPException(
                status_code=400,
                detail="Billing period must be 'monthly' or 'yearly'"
            )
        
        # Get the price for this plan and billing period
        price = db.query(PlanPrice).filter_by(
            plan_id=plan.id,
            billing_period=request.billing_period
        ).first()
        
        if not price:
            raise HTTPException(
                status_code=404,
                detail=f"Price not found for plan '{request.plan_code}' with billing period '{request.billing_period}'"
            )
        
        # For free plan or testing, automatically approve
        # For paid plans in production, you'd verify payment first
        trial_days = price.trial_days if price.price_cents > 0 else 0
        
        # Create or update subscription
        subscription = PlanService.create_subscription(
            db=db,
            user_id=request.user_id,
            plan_code=request.plan_code,
            billing_period=request.billing_period,
            trial_days=trial_days
        )
        
        return {
            "success": True,
            "message": f"Successfully subscribed to {plan.name} plan",
            "subscription": {
                "plan_code": plan.code,
                "plan_name": plan.name,
                "billing_period": subscription.billing_period,
                "status": subscription.status.value,
                "price_cents": price.price_cents,
                "currency": price.currency,
                "current_period_start": subscription.current_period_start.isoformat(),
                "current_period_end": subscription.current_period_end.isoformat(),
                "trial_ends_at": subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None,
                "is_trial": subscription.trial_ends_at is not None and subscription.trial_ends_at > datetime.utcnow() if subscription.trial_ends_at else False
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create subscription: {str(e)}"
        )

