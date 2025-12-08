"""
Clerk authentication service for validating tokens and managing user roles.
"""
import os
from typing import Optional
from fastapi import HTTPException, Header
from sqlalchemy.orm import Session
import httpx

from app.models import User, UserRole
from app.config import settings


class ClerkAuthService:
    """Service for Clerk authentication and user management."""
    
    # Clerk API base URL
    CLERK_API_BASE = "https://api.clerk.com/v1"
    
    @staticmethod
    def get_clerk_secret_key() -> str:
        """Get Clerk secret key from environment."""
        key = os.getenv("CLERK_SECRET_KEY") or settings.__dict__.get("clerk_secret_key")
        if not key:
            raise HTTPException(
                status_code=500,
                detail="CLERK_SECRET_KEY not configured"
            )
        return key
    
    @staticmethod
    async def verify_token(token: str) -> dict:
        """
        Verify Clerk JWT token and return user info.
        
        For now, we decode the JWT without verification (for development).
        In production, verify the JWT signature using Clerk's public key.
        
        Args:
            token: Clerk JWT token from Authorization header
            
        Returns:
            Dict with user info: { "user_id": str, "email": str, "full_name": str }
            
        Raises:
            HTTPException if token is invalid
        """
        try:
            import base64
            import json
            
            # Decode JWT (without verification for now)
            # JWT format: header.payload.signature
            parts = token.split(".")
            if len(parts) != 3:
                raise HTTPException(status_code=401, detail="Invalid token format")
            
            # Decode payload (base64url)
            payload_b64 = parts[1]
            # Add padding if needed
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64)
            payload = json.loads(payload_json)
            
            # Extract user info from token
            user_id = payload.get("sub") or payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Token missing user ID")
            
            return {
                "user_id": user_id,
                "email": payload.get("email", ""),
                "full_name": payload.get("name") or payload.get("full_name")
            }
                
        except json.JSONDecodeError:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Token verification failed: {str(e)}"
            )
    
    @staticmethod
    async def get_user_from_token(
        authorization: Optional[str] = Header(None)
    ) -> dict:
        """
        Extract and verify token from Authorization header.
        
        Args:
            authorization: Authorization header value (Bearer <token>)
            
        Returns:
            Dict with user info from token
        """
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )
        
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format. Expected: Bearer <token>"
            )
        
        token = parts[1]
        return await ClerkAuthService.verify_token(token)
    
    @staticmethod
    def get_or_create_user_from_clerk(
        db: Session,
        clerk_user_id: str,
        email: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        Get or create a user from Clerk data.
        
        Args:
            db: Database session
            clerk_user_id: Clerk user ID
            email: User email
            full_name: User full name (optional)
            
        Returns:
            User model instance
        """
        # Try to find existing user
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        
        if user:
            # Update email and name if provided
            if email and user.email != email:
                user.email = email
            if full_name and user.full_name != full_name:
                user.full_name = full_name
            db.commit()
            return user
        
        # Create new user
        user = User(
            clerk_user_id=clerk_user_id,
            email=email,
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_clerk_id(db: Session, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID."""
        return db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
    
    @staticmethod
    def set_user_role(db: Session, user_id: str, role: UserRole) -> User:
        """
        Set user role.
        
        Args:
            db: Database session
            user_id: User ID
            role: UserRole enum value
            
        Returns:
            Updated User model instance
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.role = role
        db.commit()
        db.refresh(user)
        return user

