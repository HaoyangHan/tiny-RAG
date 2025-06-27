"""
User management routes for TinyRAG v1.4.

This module contains user-related API endpoints for user management and profiles.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from auth.models import User, UserResponse, UserUpdate
from auth.service import get_current_user, get_current_active_user
from .service import UserService

router = APIRouter()


class UserProfileResponse(BaseModel):
    """Extended user profile response."""
    
    id: str = Field(description="User ID")
    email: str = Field(description="User email")
    username: str = Field(description="Username")
    full_name: str = Field(description="Full name")
    role: str = Field(description="User role")
    status: str = Field(description="User status")
    created_at: str = Field(description="Account creation timestamp")
    last_login: Optional[str] = Field(description="Last login timestamp")
    project_count: int = Field(description="Number of projects owned")
    collaboration_count: int = Field(description="Number of projects collaborating on")


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="Get user profile",
    description="Get detailed profile information for the current user"
)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> UserProfileResponse:
    """Get detailed user profile."""
    try:
        user_service = UserService()
        
        # Get basic profile
        profile = await user_service.get_user_profile(str(current_user.id))
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Get dashboard stats for project counts
        stats = await user_service.get_user_dashboard_stats(str(current_user.id))
        project_count = stats.get("projects", {}).get("owned", 0)
        collaboration_count = stats.get("projects", {}).get("collaborated", 0)
        
        return UserProfileResponse(
            id=profile["id"],
            email=profile["email"],
            username=profile["username"],
            full_name=profile["full_name"],
            role=current_user.role.value,
            status=current_user.status.value,
            created_at=profile["created_at"] or "",
            last_login=profile["last_login"],
            project_count=project_count,
            collaboration_count=collaboration_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.get(
    "/analytics",
    summary="Get user analytics",
    description="Get analytics and statistics for the current user"
)
async def get_user_analytics(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Get user analytics and statistics."""
    try:
        user_service = UserService()
        stats = await user_service.get_user_dashboard_stats(str(current_user.id))
        
        if not stats:
            return {
                "projects": {"total": 0, "owned": 0, "collaborated": 0, "recent": 0},
                "elements": {"total": 0, "recent": 0, "by_type": {}},
                "generations": {"total": 0, "recent": 0, "total_tokens": 0, "total_cost_usd": 0.0},
                "evaluations": {"total": 0, "recent": 0, "completed": 0, "average_score": 0.0}
            }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user analytics: {str(e)}"
        )


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update current user's profile information"
)
async def update_user_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Update user profile."""
    try:
        user_service = UserService()
        
        # Convert UserUpdate to dict
        update_data = {}
        if updates.username is not None:
            update_data["username"] = updates.username
        if updates.full_name is not None:
            update_data["full_name"] = updates.full_name
        
        # Update profile
        updated_profile = await user_service.update_user_profile(
            str(current_user.id),
            update_data
        )
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or update failed"
            )
        
        # Return updated user
        updated_user = await User.get(current_user.id)
        return UserResponse(
            id=str(updated_user.id),
            email=updated_user.email,
            username=updated_user.username,
            full_name=updated_user.full_name,
            role=updated_user.role,
            status=updated_user.status,
            created_at=updated_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )


@router.get(
    "/search",
    response_model=List[UserResponse],
    summary="Search users",
    description="Search for users by username or email (for collaboration)"
)
async def search_users(
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user)
) -> List[UserResponse]:
    """Search for users."""
    try:
        user_service = UserService()
        users = await user_service.search_users(query, limit, str(current_user.id))
        
        return [
            UserResponse(
                id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role=user.role,
                status=user.status,
                created_at=user.created_at
            )
            for user in users
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get public user information by user ID"
)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Get user information by ID."""
    try:
        from beanie import PydanticObjectId
        
        # Convert string to ObjectId and get user by ID
        user = await User.get(PydanticObjectId(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return public user information
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        ) 