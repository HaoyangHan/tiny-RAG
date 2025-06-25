"""
User service for TinyRAG v1.4.

This module contains the business logic for user management including
profile management, settings, project analytics, and user statistics.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from beanie.operators import In, And, Or

from auth.models import User
from models import Project, Element, ElementGeneration, Evaluation

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user management operations.
    
    Handles all business logic related to users including profile management,
    settings, analytics, and user statistics for the v1.4 architecture.
    """
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile with basic information.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: User profile information if found, None otherwise
        """
        try:
            user = await User.get(PydanticObjectId(user_id))
            
            if not user:
                return None
            
            return {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.status.value == "active",
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get user profile {user_id}: {str(e)}")
            return None
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile information.
        
        Args:
            user_id: User ID
            updates: Dictionary of updates to apply
            
        Returns:
            Dict[str, Any]: Updated user profile if successful, None otherwise
        """
        try:
            user = await User.get(PydanticObjectId(user_id))
            
            if not user:
                return None
            
            # Apply allowed updates
            allowed_fields = {'username', 'full_name'}
            for field, value in updates.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            # Save changes
            await user.save()
            
            logger.info(f"Updated user profile {user_id}")
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Failed to update user profile {user_id}: {str(e)}")
            return None
    
    async def get_user_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get dashboard statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Dashboard statistics
        """
        try:
            # Get user's projects (owned and collaborated)
            user_projects = await Project.find(
                And(
                    Project.is_deleted == False,
                    Or(
                        Project.owner_id == user_id,
                        In(Project.collaborators, [user_id])
                    )
                )
            ).to_list()
            
            owned_projects = [p for p in user_projects if p.owner_id == user_id]
            collaborated_projects = [p for p in user_projects if p.owner_id != user_id]
            
            # Get project IDs for further queries
            project_ids = [str(p.id) for p in user_projects]
            
            # Get elements in user's projects
            if project_ids:
                user_elements = await Element.find(
                    And(
                        Element.is_deleted == False,
                        In(Element.project_id, project_ids)
                    )
                ).to_list()
                
                # Get generations in user's projects
                user_generations = await ElementGeneration.find(
                    And(
                        ElementGeneration.is_deleted == False,
                        In(ElementGeneration.project_id, project_ids)
                    )
                ).to_list()
                
                # Get evaluations in user's projects
                user_evaluations = await Evaluation.find(
                    And(
                        Evaluation.is_deleted == False,
                        In(Evaluation.project_id, project_ids)
                    )
                ).to_list()
            else:
                user_elements = []
                user_generations = []
                user_evaluations = []
            
            # Calculate recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_elements = [e for e in user_elements if e.created_at >= week_ago]
            recent_generations = [g for g in user_generations if g.created_at >= week_ago]
            recent_evaluations = [e for e in user_evaluations if e.created_at >= week_ago]
            
            # Calculate total usage statistics
            total_tokens = sum(g.metrics.total_tokens for g in user_generations if g.metrics)
            total_cost = sum(g.metrics.cost_usd for g in user_generations if g.metrics)
            
            # Calculate average evaluation score
            completed_evaluations = [e for e in user_evaluations if e.overall_score is not None]
            avg_evaluation_score = (
                sum(e.overall_score for e in completed_evaluations) / len(completed_evaluations)
                if completed_evaluations else 0.0
            )
            
            return {
                "projects": {
                    "total": len(user_projects),
                    "owned": len(owned_projects),
                    "collaborated": len(collaborated_projects),
                    "recent": len([p for p in user_projects if p.created_at >= week_ago])
                },
                "elements": {
                    "total": len(user_elements),
                    "recent": len(recent_elements),
                    "by_type": self._count_by_attribute(user_elements, 'element_type')
                },
                "generations": {
                    "total": len(user_generations),
                    "recent": len(recent_generations),
                    "total_tokens": total_tokens,
                    "total_cost_usd": round(total_cost, 4)
                },
                "evaluations": {
                    "total": len(user_evaluations),
                    "recent": len(recent_evaluations),
                    "completed": len(completed_evaluations),
                    "average_score": round(avg_evaluation_score, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get user dashboard stats {user_id}: {str(e)}")
            return {}
    
    async def get_user_project_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user's project activity over time.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Project activity analytics
        """
        try:
            # Get date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user's projects
            user_projects = await Project.find(
                And(
                    Project.is_deleted == False,
                    Or(
                        Project.owner_id == user_id,
                        In(Project.collaborators, [user_id])
                    ),
                    Project.created_at >= start_date
                )
            ).to_list()
            
            project_ids = [str(p.id) for p in user_projects]
            
            # Get activities in date range
            if project_ids:
                elements = await Element.find(
                    And(
                        Element.is_deleted == False,
                        In(Element.project_id, project_ids),
                        Element.created_at >= start_date
                    )
                ).to_list()
                
                generations = await ElementGeneration.find(
                    And(
                        ElementGeneration.is_deleted == False,
                        In(ElementGeneration.project_id, project_ids),
                        ElementGeneration.created_at >= start_date
                    )
                ).to_list()
                
                evaluations = await Evaluation.find(
                    And(
                        Evaluation.is_deleted == False,
                        In(Evaluation.project_id, project_ids),
                        Evaluation.created_at >= start_date
                    )
                ).to_list()
            else:
                elements = []
                generations = []
                evaluations = []
            
            # Group by date
            activity_by_date = {}
            
            for i in range(days):
                date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                activity_by_date[date] = {
                    "projects": 0,
                    "elements": 0,
                    "generations": 0,
                    "evaluations": 0
                }
            
            # Count activities by date
            for project in user_projects:
                date = project.created_at.strftime('%Y-%m-%d')
                if date in activity_by_date:
                    activity_by_date[date]["projects"] += 1
            
            for element in elements:
                date = element.created_at.strftime('%Y-%m-%d')
                if date in activity_by_date:
                    activity_by_date[date]["elements"] += 1
            
            for generation in generations:
                date = generation.created_at.strftime('%Y-%m-%d')
                if date in activity_by_date:
                    activity_by_date[date]["generations"] += 1
            
            for evaluation in evaluations:
                date = evaluation.created_at.strftime('%Y-%m-%d')
                if date in activity_by_date:
                    activity_by_date[date]["evaluations"] += 1
            
            return {
                "period": f"{days} days",
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "activity": activity_by_date,
                "totals": {
                    "projects": len(user_projects),
                    "elements": len(elements),
                    "generations": len(generations),
                    "evaluations": len(evaluations)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get user activity {user_id}: {str(e)}")
            return {}
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences and settings.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: User preferences
        """
        try:
            # For now, return default preferences
            # In the future, this could be stored in a UserPreferences model
            return {
                "theme": "light",
                "language": "en",
                "notifications": {
                    "email": True,
                    "push": False,
                    "evaluation_complete": True,
                    "generation_complete": True
                },
                "dashboard": {
                    "default_view": "overview",
                    "items_per_page": 20,
                    "show_analytics": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get user preferences {user_id}: {str(e)}")
            return {}
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user preferences.
        
        Args:
            user_id: User ID
            preferences: New preferences
            
        Returns:
            Dict[str, Any]: Updated preferences
        """
        try:
            # For now, just return the input preferences
            # In the future, this would be stored in database
            logger.info(f"Updated preferences for user {user_id}")
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to update user preferences {user_id}: {str(e)}")
            return {}
    
    def _count_by_attribute(self, items: List, attribute: str) -> Dict[str, int]:
        """
        Count items by a specific attribute.
        
        Args:
            items: List of items
            attribute: Attribute to count by
            
        Returns:
            Dict[str, int]: Count by attribute value
        """
        counts = {}
        for item in items:
            value = getattr(item, attribute, 'unknown')
            value_str = str(value) if value else 'unknown'
            counts[value_str] = counts.get(value_str, 0) + 1
        return counts 