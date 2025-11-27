"""
Token Usage Service - Tracks LLM token usage and calculates costs.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models import TokenUsageLog, ModelPricing
from app.services.plan_service import PlanService


class TokenUsageService:
    """Service for logging and analyzing LLM token usage."""
    
    @staticmethod
    def log_token_usage(
        db: Session,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        user_id: Optional[str] = None,
        feature_code: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TokenUsageLog:
        """
        Log token usage from an LLM API call and calculate cost.
        
        Args:
            db: Database session
            model_name: LLM model name (e.g., 'gpt-4o')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            user_id: Optional user ID
            feature_code: Optional feature code
            request_id: Optional request ID for tracing
            metadata: Optional metadata dictionary
            
        Returns:
            TokenUsageLog object
        """
        # Get model pricing
        model_pricing = db.query(ModelPricing).filter_by(model_name=model_name).first()
        
        if not model_pricing:
            # Model not found - use default pricing or create warning
            print(f"⚠️  Model '{model_name}' not found in pricing table. Using default rates.")
            # Default to conservative pricing
            input_cost = 0.0001  # $0.10 per 1K tokens
            output_cost = 0.0001
        else:
            input_cost = model_pricing.input_cost_per_1k
            output_cost = model_pricing.output_cost_per_1k
        
        # Calculate cost
        cost_usd = TokenUsageService._calculate_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_per_1k=input_cost,
            output_cost_per_1k=output_cost
        )
        
        # Get user's plan ID if available
        plan_id = None
        if user_id:
            try:
                plan = PlanService.get_user_plan(db, user_id)
                plan_id = plan.id
            except Exception:
                pass
        
        # Create log entry
        log_entry = TokenUsageLog(
            user_id=user_id,
            plan_id=plan_id,
            feature_code=feature_code,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            request_id=request_id,
            metadata_json=metadata
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        return log_entry
    
    @staticmethod
    def _calculate_cost(
        input_tokens: int,
        output_tokens: int,
        input_cost_per_1k: float,
        output_cost_per_1k: float
    ) -> float:
        """
        Calculate cost in USD from token counts.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_cost_per_1k: Cost per 1000 input tokens
            output_cost_per_1k: Cost per 1000 output tokens
            
        Returns:
            Total cost in USD
        """
        input_cost = (input_tokens / 1000.0) * input_cost_per_1k
        output_cost = (output_tokens / 1000.0) * output_cost_per_1k
        return round(input_cost + output_cost, 6)
    
    @staticmethod
    def get_user_cost_summary(
        db: Session,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get cost summary for a user over a period.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Dictionary with cost summary
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get total cost
        total_cost = db.query(func.sum(TokenUsageLog.cost_usd)).filter(
            TokenUsageLog.user_id == user_id,
            TokenUsageLog.created_at >= start_date
        ).scalar() or 0.0
        
        # Get total tokens
        total_input = db.query(func.sum(TokenUsageLog.input_tokens)).filter(
            TokenUsageLog.user_id == user_id,
            TokenUsageLog.created_at >= start_date
        ).scalar() or 0
        
        total_output = db.query(func.sum(TokenUsageLog.output_tokens)).filter(
            TokenUsageLog.user_id == user_id,
            TokenUsageLog.created_at >= start_date
        ).scalar() or 0
        
        # Get usage by model
        model_usage = db.query(
            TokenUsageLog.model_name,
            func.sum(TokenUsageLog.input_tokens).label('input_tokens'),
            func.sum(TokenUsageLog.output_tokens).label('output_tokens'),
            func.sum(TokenUsageLog.cost_usd).label('cost'),
            func.count(TokenUsageLog.id).label('requests')
        ).filter(
            TokenUsageLog.user_id == user_id,
            TokenUsageLog.created_at >= start_date
        ).group_by(TokenUsageLog.model_name).all()
        
        # Get usage by feature
        feature_usage = db.query(
            TokenUsageLog.feature_code,
            func.sum(TokenUsageLog.cost_usd).label('cost'),
            func.count(TokenUsageLog.id).label('requests')
        ).filter(
            TokenUsageLog.user_id == user_id,
            TokenUsageLog.created_at >= start_date,
            TokenUsageLog.feature_code.isnot(None)
        ).group_by(TokenUsageLog.feature_code).all()
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "by_model": [
                {
                    "model": row.model_name,
                    "input_tokens": row.input_tokens,
                    "output_tokens": row.output_tokens,
                    "cost_usd": round(row.cost, 4),
                    "requests": row.requests
                }
                for row in model_usage
            ],
            "by_feature": [
                {
                    "feature_code": row.feature_code,
                    "cost_usd": round(row.cost, 4),
                    "requests": row.requests
                }
                for row in feature_usage
            ]
        }
    
    @staticmethod
    def get_total_cost_summary(
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get overall cost summary across all users (for admin).
        
        Args:
            db: Database session
            days: Number of days to look back
            
        Returns:
            Dictionary with cost summary
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total cost
        total_cost = db.query(func.sum(TokenUsageLog.cost_usd)).filter(
            TokenUsageLog.created_at >= start_date
        ).scalar() or 0.0
        
        # Total tokens
        total_input = db.query(func.sum(TokenUsageLog.input_tokens)).filter(
            TokenUsageLog.created_at >= start_date
        ).scalar() or 0
        
        total_output = db.query(func.sum(TokenUsageLog.output_tokens)).filter(
            TokenUsageLog.created_at >= start_date
        ).scalar() or 0
        
        # Total requests
        total_requests = db.query(func.count(TokenUsageLog.id)).filter(
            TokenUsageLog.created_at >= start_date
        ).scalar() or 0
        
        # Unique users
        unique_users = db.query(func.count(func.distinct(TokenUsageLog.user_id))).filter(
            TokenUsageLog.created_at >= start_date,
            TokenUsageLog.user_id.isnot(None)
        ).scalar() or 0
        
        # By model
        model_usage = db.query(
            TokenUsageLog.model_name,
            func.sum(TokenUsageLog.input_tokens).label('input_tokens'),
            func.sum(TokenUsageLog.output_tokens).label('output_tokens'),
            func.sum(TokenUsageLog.cost_usd).label('cost'),
            func.count(TokenUsageLog.id).label('requests')
        ).filter(
            TokenUsageLog.created_at >= start_date
        ).group_by(TokenUsageLog.model_name).all()
        
        # By feature
        feature_usage = db.query(
            TokenUsageLog.feature_code,
            func.sum(TokenUsageLog.cost_usd).label('cost'),
            func.count(TokenUsageLog.id).label('requests')
        ).filter(
            TokenUsageLog.created_at >= start_date,
            TokenUsageLog.feature_code.isnot(None)
        ).group_by(TokenUsageLog.feature_code).all()
        
        # Daily breakdown
        daily_usage = db.query(
            func.date(TokenUsageLog.created_at).label('date'),
            func.sum(TokenUsageLog.cost_usd).label('cost'),
            func.count(TokenUsageLog.id).label('requests')
        ).filter(
            TokenUsageLog.created_at >= start_date
        ).group_by(func.date(TokenUsageLog.created_at)).order_by(func.date(TokenUsageLog.created_at)).all()
        
        return {
            "period_days": days,
            "period_start": start_date.isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "total_cost_usd": round(total_cost, 4),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_requests": total_requests,
            "unique_users": unique_users,
            "avg_cost_per_request": round(total_cost / total_requests, 6) if total_requests > 0 else 0,
            "by_model": [
                {
                    "model": row.model_name,
                    "input_tokens": row.input_tokens,
                    "output_tokens": row.output_tokens,
                    "cost_usd": round(row.cost, 4),
                    "requests": row.requests
                }
                for row in model_usage
            ],
            "by_feature": [
                {
                    "feature_code": row.feature_code,
                    "cost_usd": round(row.cost, 4),
                    "requests": row.requests
                }
                for row in feature_usage
            ],
            "daily": [
                {
                    "date": row.date.isoformat(),
                    "cost_usd": round(row.cost, 4),
                    "requests": row.requests
                }
                for row in daily_usage
            ]
        }
    
    @staticmethod
    def seed_model_pricing(db: Session) -> None:
        """
        Seed database with current OpenAI model pricing.
        Call this during initial setup or when prices change.
        """
        models = [
            {
                "model_name": "gpt-4o",
                "input_cost_per_1k": 0.0025,  # $2.50 per 1M tokens
                "output_cost_per_1k": 0.010,   # $10.00 per 1M tokens
            },
            {
                "model_name": "gpt-4o-mini",
                "input_cost_per_1k": 0.00015,  # $0.15 per 1M tokens
                "output_cost_per_1k": 0.0006,   # $0.60 per 1M tokens
            },
            {
                "model_name": "gpt-4-turbo",
                "input_cost_per_1k": 0.010,     # $10.00 per 1M tokens
                "output_cost_per_1k": 0.030,    # $30.00 per 1M tokens
            },
            {
                "model_name": "gpt-3.5-turbo",
                "input_cost_per_1k": 0.0005,    # $0.50 per 1M tokens
                "output_cost_per_1k": 0.0015,   # $1.50 per 1M tokens
            },
        ]
        
        for model_data in models:
            existing = db.query(ModelPricing).filter_by(model_name=model_data["model_name"]).first()
            if not existing:
                model_pricing = ModelPricing(**model_data)
                db.add(model_pricing)
                print(f"✅ Added pricing for {model_data['model_name']}")
            else:
                # Update existing
                existing.input_cost_per_1k = model_data["input_cost_per_1k"]
                existing.output_cost_per_1k = model_data["output_cost_per_1k"]
                existing.updated_at = datetime.utcnow()
                print(f"✅ Updated pricing for {model_data['model_name']}")
        
        db.commit()
        print("✅ Model pricing seeded successfully!")

