"""
Evaluation service for TinyRAG v1.4.

This module contains the business logic for evaluation management including
CRUD operations, LLM-as-a-judge integration, scoring, and analytics.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId
from beanie.operators import In, And, Or

from models import (
    Evaluation, EvaluationCriteria, EvaluationScore, EvaluationResult,
    ElementGeneration, Project, EvaluationStatus
)

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Service class for evaluation management operations.
    
    Handles all business logic related to evaluations including creation,
    retrieval, updates, deletion, LLM-as-a-judge integration, and analytics.
    """
    
    async def create_evaluation(
        self,
        generation_id: str,
        criteria: List[EvaluationCriteria],
        user_id: str,
        evaluation_config: Optional[Dict[str, Any]] = None
    ) -> Evaluation:
        """
        Create a new evaluation for a generation.
        
        Args:
            generation_id: Associated generation ID
            criteria: List of evaluation criteria
            user_id: ID of the requesting user
            evaluation_config: Optional configuration for evaluation
            
        Returns:
            Evaluation: Created evaluation instance
            
        Raises:
            ValueError: If validation fails
            Exception: If creation fails
        """
        try:
            # Verify generation exists and user has access
            generation = await ElementGeneration.get(PydanticObjectId(generation_id))
            if not generation or generation.is_deleted:
                raise ValueError("Generation not found")
            
            # Check project access
            project = await Project.get(PydanticObjectId(generation.project_id))
            if not project or not project.is_accessible_by(user_id):
                raise ValueError("Access denied to associated project")
            
            # Validate criteria
            if not criteria:
                raise ValueError("At least one evaluation criterion is required")
            
            # Create evaluation instance
            evaluation = Evaluation(
                generation_id=generation_id,
                project_id=generation.project_id,
                criteria=criteria,
                status=EvaluationStatus.PENDING,
                config=evaluation_config or {},
                evaluator_id=user_id
            )
            
            # Save to database
            await evaluation.insert()
            
            # Add to project
            project.add_evaluation(str(evaluation.id))
            await project.save()
            
            logger.info(f"Created evaluation {evaluation.id} for generation {generation_id}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Failed to create evaluation: {str(e)}")
            raise
    
    async def get_evaluation(self, evaluation_id: str, user_id: str) -> Optional[Evaluation]:
        """
        Get an evaluation by ID with access control.
        
        Args:
            evaluation_id: Evaluation ID to retrieve
            user_id: ID of the requesting user
            
        Returns:
            Evaluation: Evaluation instance if found and accessible, None otherwise
        """
        try:
            evaluation = await Evaluation.get(PydanticObjectId(evaluation_id))
            
            if not evaluation or evaluation.is_deleted:
                return None
            
            # Check project access
            project = await Project.get(PydanticObjectId(evaluation.project_id))
            if not project or not project.is_accessible_by(user_id):
                return None
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Failed to get evaluation {evaluation_id}: {str(e)}")
            return None
    
    async def list_evaluations(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        project_id: Optional[str] = None,
        generation_id: Optional[str] = None,
        status: Optional[EvaluationStatus] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None
    ) -> Tuple[List[Evaluation], int]:
        """
        List evaluations accessible to a user with filtering and pagination.
        
        Args:
            user_id: ID of the requesting user
            page: Page number (1-based)
            page_size: Number of items per page
            project_id: Filter by project ID
            generation_id: Filter by generation ID
            status: Filter by evaluation status
            min_score: Minimum overall score filter
            max_score: Maximum overall score filter
            
        Returns:
            Tuple[List[Evaluation], int]: List of evaluations and total count
        """
        try:
            # Build query conditions
            conditions = [Evaluation.is_deleted == False]
            
            # Get accessible project IDs
            if project_id:
                # Check specific project access
                project = await Project.get(PydanticObjectId(project_id))
                if not project or not project.is_accessible_by(user_id):
                    return [], 0
                conditions.append(Evaluation.project_id == project_id)
            else:
                # Get all accessible projects
                accessible_projects = await self._get_accessible_project_ids(user_id)
                if not accessible_projects:
                    return [], 0
                conditions.append(In(Evaluation.project_id, accessible_projects))
            
            # Apply filters
            if generation_id:
                conditions.append(Evaluation.generation_id == generation_id)
            
            if status:
                conditions.append(Evaluation.status == status)
            
            if min_score is not None:
                conditions.append(Evaluation.overall_score >= min_score)
            
            if max_score is not None:
                conditions.append(Evaluation.overall_score <= max_score)
            
            # Build final query
            query = Evaluation.find(And(*conditions))
            
            # Get total count
            total_count = await query.count()
            
            # Apply pagination and sorting
            evaluations = await query.sort(-Evaluation.updated_at).skip((page - 1) * page_size).limit(page_size).to_list()
            
            return evaluations, total_count
            
        except Exception as e:
            logger.error(f"Failed to list evaluations for user {user_id}: {str(e)}")
            return [], 0
    
    async def update_evaluation_status(
        self,
        evaluation_id: str,
        status: EvaluationStatus,
        user_id: str,
        error_message: Optional[str] = None
    ) -> Optional[Evaluation]:
        """
        Update evaluation status.
        
        Args:
            evaluation_id: Evaluation ID to update
            status: New status
            user_id: ID of the requesting user
            error_message: Optional error message if status is FAILED
            
        Returns:
            Evaluation: Updated evaluation instance if successful, None otherwise
        """
        try:
            evaluation = await self.get_evaluation(evaluation_id, user_id)
            
            if not evaluation:
                return None
            
            # Update status
            evaluation.status = status
            
            if error_message:
                evaluation.error_message = error_message
            
            if status == EvaluationStatus.COMPLETED:
                evaluation.evaluated_at = datetime.utcnow()
            
            # Update timestamp
            evaluation.update_timestamp()
            
            # Save changes
            await evaluation.save()
            
            logger.info(f"Updated evaluation {evaluation_id} status to {status}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Failed to update evaluation status {evaluation_id}: {str(e)}")
            return None
    
    async def add_evaluation_result(
        self,
        evaluation_id: str,
        result: EvaluationResult,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Add evaluation result with scores.
        
        Args:
            evaluation_id: Evaluation ID
            result: Evaluation result with scores
            user_id: ID of the requesting user (optional for system updates)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            evaluation = await Evaluation.get(PydanticObjectId(evaluation_id))
            
            if not evaluation or evaluation.is_deleted:
                return False
            
            # If user_id provided, check access
            if user_id:
                project = await Project.get(PydanticObjectId(evaluation.project_id))
                if not project or not project.is_accessible_by(user_id):
                    return False
            
            # Add result to evaluation
            evaluation.add_result(result)
            
            # Calculate overall score
            evaluation.calculate_overall_score()
            
            # Update status if completed
            if evaluation.status == EvaluationStatus.PENDING:
                evaluation.status = EvaluationStatus.COMPLETED
                evaluation.evaluated_at = datetime.utcnow()
            
            # Update timestamp
            evaluation.update_timestamp()
            
            # Save changes
            await evaluation.save()
            
            logger.info(f"Added result to evaluation {evaluation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add result to evaluation {evaluation_id}: {str(e)}")
            return False
    
    async def delete_evaluation(self, evaluation_id: str, user_id: str) -> bool:
        """
        Delete an evaluation (soft delete) with access control.
        
        Args:
            evaluation_id: Evaluation ID to delete
            user_id: ID of the requesting user
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            evaluation = await Evaluation.get(PydanticObjectId(evaluation_id))
            
            if not evaluation or evaluation.is_deleted:
                return False
            
            # Check project access
            project = await Project.get(PydanticObjectId(evaluation.project_id))
            if not project or not project.is_accessible_by(user_id):
                return False
            
            # Only evaluator or project owner can delete
            if evaluation.evaluator_id != user_id and project.owner_id != user_id:
                return False
            
            # Perform soft delete
            evaluation.mark_deleted()
            await evaluation.save()
            
            # Remove from project
            project.remove_evaluation(evaluation_id)
            await project.save()
            
            logger.info(f"Deleted evaluation {evaluation_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete evaluation {evaluation_id}: {str(e)}")
            return False
    
    async def get_evaluation_analytics(
        self,
        user_id: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get evaluation analytics for a user or project.
        
        Args:
            user_id: ID of the requesting user
            project_id: Optional project ID to filter analytics
            
        Returns:
            Dict[str, Any]: Evaluation analytics
        """
        try:
            # Get accessible project IDs
            if project_id:
                project = await Project.get(PydanticObjectId(project_id))
                if not project or not project.is_accessible_by(user_id):
                    return {}
                accessible_projects = [project_id]
            else:
                accessible_projects = await self._get_accessible_project_ids(user_id)
            
            if not accessible_projects:
                return {}
            
            # Build query for completed evaluations
            query = Evaluation.find(
                And(
                    Evaluation.is_deleted == False,
                    Evaluation.status == EvaluationStatus.COMPLETED,
                    In(Evaluation.project_id, accessible_projects)
                )
            )
            
            evaluations = await query.to_list()
            
            if not evaluations:
                return {
                    "total_evaluations": 0,
                    "average_score": 0.0,
                    "score_distribution": {},
                    "criteria_performance": {}
                }
            
            # Calculate analytics
            total_evaluations = len(evaluations)
            scores = [eval.overall_score for eval in evaluations if eval.overall_score is not None]
            average_score = sum(scores) / len(scores) if scores else 0.0
            
            # Score distribution (0-20, 20-40, 40-60, 60-80, 80-100)
            score_ranges = {
                "0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0
            }
            
            for score in scores:
                if score <= 20:
                    score_ranges["0-20"] += 1
                elif score <= 40:
                    score_ranges["20-40"] += 1
                elif score <= 60:
                    score_ranges["40-60"] += 1
                elif score <= 80:
                    score_ranges["60-80"] += 1
                else:
                    score_ranges["80-100"] += 1
            
            # Criteria performance
            criteria_scores = {}
            for evaluation in evaluations:
                if evaluation.result and evaluation.result.scores:
                    for score in evaluation.result.scores:
                        if score.criterion_name not in criteria_scores:
                            criteria_scores[score.criterion_name] = []
                        criteria_scores[score.criterion_name].append(score.score)
            
            criteria_performance = {
                criterion: {
                    "average": sum(scores) / len(scores),
                    "count": len(scores)
                }
                for criterion, scores in criteria_scores.items()
            }
            
            return {
                "total_evaluations": total_evaluations,
                "average_score": round(average_score, 2),
                "score_distribution": score_ranges,
                "criteria_performance": criteria_performance
            }
            
        except Exception as e:
            logger.error(f"Failed to get evaluation analytics: {str(e)}")
            return {}
    
    async def _get_accessible_project_ids(self, user_id: str) -> List[str]:
        """
        Get list of project IDs accessible to a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[str]: List of accessible project IDs
        """
        try:
            # Get projects user owns, collaborates on, or are public
            projects = await Project.find(
                And(
                    Project.is_deleted == False,
                    Or(
                        Project.owner_id == user_id,
                        In(Project.collaborators, [user_id]),
                        Project.visibility == "public"
                    )
                )
            ).to_list()
            
            return [str(project.id) for project in projects]
            
        except Exception as e:
            logger.error(f"Failed to get accessible projects for user {user_id}: {str(e)}")
            return [] 