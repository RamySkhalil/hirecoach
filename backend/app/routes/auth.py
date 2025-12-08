"""
Authentication routes for Clerk integration and user role management.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.db import get_db
from app.models import User, UserRole
from app.services.auth_service import ClerkAuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SyncUserRequest(BaseModel):
    """Request to sync user from Clerk."""
    clerk_user_id: str
    email: str
    full_name: Optional[str] = None


class SyncUserResponse(BaseModel):
    """Response after syncing user."""
    id: str
    email: str
    full_name: Optional[str]
    role: Optional[str]


class SetRoleRequest(BaseModel):
    """Request to set user role."""
    role: str  # "RECRUITER" or "CANDIDATE"


class SetRoleResponse(BaseModel):
    """Response after setting role."""
    id: str
    email: str
    full_name: Optional[str]
    role: str


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    full_name: Optional[str]
    role: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# Helper Functions
# ============================================================================

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user.
    
    Validates Clerk token and returns User model.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    try:
        # Verify token and get user info
        token_info = await ClerkAuthService.get_user_from_token(authorization)
        clerk_user_id = token_info.get("user_id")
        
        if not clerk_user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get or create user
        user = ClerkAuthService.get_user_by_clerk_id(db, clerk_user_id)
        if not user:
            # Create user if doesn't exist
            user = ClerkAuthService.get_or_create_user_from_clerk(
                db,
                clerk_user_id,
                token_info.get("email", ""),
                token_info.get("full_name")
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )


def require_role(required_role: UserRole):
    """
    Dependency factory to require a specific role.
    
    Usage:
        @router.get("/recruiter-only")
        def recruiter_endpoint(user: User = Depends(require_role(UserRole.RECRUITER))):
            ...
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"This endpoint requires {required_role.value} role"
            )
        return user
    return role_checker


# ============================================================================
# Routes
# ============================================================================

@router.post("/sync-user", response_model=SyncUserResponse)
async def sync_user(
    request: SyncUserRequest,
    db: Session = Depends(get_db)
):
    """
    Sync user from Clerk to our database.
    
    This endpoint should be called after user signs in to ensure
    the user exists in our database.
    Does NOT require authentication - called with Clerk user ID.
    """
    try:
        user = ClerkAuthService.get_or_create_user_from_clerk(
            db,
            request.clerk_user_id,
            request.email,
            request.full_name
        )
        
        return SyncUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value if user.role else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync user: {str(e)}"
        )


@router.post("/set-role", response_model=SetRoleResponse)
async def set_role(
    request: SetRoleRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set user role (RECRUITER or CANDIDATE).
    
    Requires authentication. Can only be called once per user
    (or we can allow role changes - your choice).
    """
    try:
        role_enum = UserRole(request.role.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be 'RECRUITER' or 'CANDIDATE'"
        )
    
    updated_user = ClerkAuthService.set_user_role(db, user.id, role_enum)
    
    # TODO: Update Clerk publicMetadata.role for convenience
    # This would require Clerk Backend SDK
    
    return SetRoleResponse(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role=updated_user.role.value
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Returns user data including role.
    """
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if user.role else None
    )

