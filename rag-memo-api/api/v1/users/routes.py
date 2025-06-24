"""
User management routes for TinyRAG v1.4.

This module contains user-related API endpoints for user management and profiles.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from auth.models import User, UserResponse, UserUpdate
from auth.service import get_current_user, get_current_active_user

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
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Get user profile",
    description="Get detailed profile information for the current user"
)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> UserProfileResponse:
    """Get detailed user profile."""
    # TODO: Get project counts from ProjectService
    project_count = 0
    collaboration_count = 0
    
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role.value,
        status=current_user.status.value,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None,
        project_count=project_count,
        collaboration_count=collaboration_count
    )


@router.put(
    "/me/profile",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update current user's profile information"
)
async def update_user_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Update user profile."""
    # TODO: Implement user profile update logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile update functionality not implemented yet"
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
    # TODO: Implement user search functionality
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User search functionality not implemented yet"
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
    # TODO: Implement get user by ID with privacy controls
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get user by ID functionality not implemented yet"
    ) 