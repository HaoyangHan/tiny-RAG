"""
Generation service for TinyRAG v1.4.

This module contains the business logic for generation management including
CRUD operations, LLM integration, performance tracking, and content management.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId
from beanie.operators import In, And, Or

from models import (
    ElementGeneration, GenerationChunk, GenerationMetrics,
    Element, Project, GenerationStatus
)

logger = logging.getLogger(__name__)


class ElementGenerationService:
    """
    Service class for generation management operations.
    
    Handles all business logic related to element generations including creation,
    retrieval, updates, deletion, LLM integration, and performance tracking.
    """
    
    async def create_generation(
        self,
        element_id: str,
        prompt: str,
        user_id: str,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> ElementGeneration:
        """
        Create a new generation.
        
        Args:
            element_id: Associated element ID
            prompt: Input prompt for generation
            user_id: ID of the requesting user
            generation_config: Optional configuration for generation
            
        Returns:
            ElementGeneration: Created generation instance
            
        Raises:
            ValueError: If validation fails
            Exception: If creation fails
        """
        try:
            # Verify element exists and user has access
            element = await Element.get(PydanticObjectId(element_id))
            if not element or element.is_deleted:
                raise ValueError("Element not found")
            
            # Check project access
            project = await Project.get(PydanticObjectId(element.project_id))
            if not project or not project.is_accessible_by(user_id):
                raise ValueError("Access denied to associated project")
            
            # Create initial metrics
            metrics = GenerationMetrics(
                total_tokens=0,
                prompt_tokens=0,
                completion_tokens=0,
                cost_usd=0.0,
                generation_time_ms=0
            )
            
            # Create generation instance
            generation = ElementGeneration(
                element_id=element_id,
                project_id=element.project_id,
                prompt=prompt,
                status=GenerationStatus.PENDING,
                metrics=metrics,
                config=generation_config or {},
                created_by=user_id
            )
            
            # Save to database
            await generation.insert()
            
            # Add to element and project
            element.add_generation(str(generation.id))
            await element.save()
            
            project.add_generation(str(generation.id))
            await project.save()
            
            logger.info(f"Created generation {generation.id} for element {element_id}")
            return generation
            
        except Exception as e:
            logger.error(f"Failed to create generation: {str(e)}")
            raise
    
    async def get_generation(self, generation_id: str, user_id: str) -> Optional[ElementGeneration]:
        """
        Get a generation by ID with access control.
        
        Args:
            generation_id: Generation ID to retrieve
            user_id: ID of the requesting user
            
        Returns:
            ElementGeneration: Generation instance if found and accessible, None otherwise
        """
        try:
            generation = await ElementGeneration.get(PydanticObjectId(generation_id))
            
            if not generation or generation.is_deleted:
                return None
            
            # Check project access
            project = await Project.get(PydanticObjectId(generation.project_id))
            if not project or not project.is_accessible_by(user_id):
                return None
            
            return generation
            
        except Exception as e:
            logger.error(f"Failed to get generation {generation_id}: {str(e)}")
            return None
    
    async def list_generations(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        project_id: Optional[str] = None,
        element_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        status: Optional[GenerationStatus] = None,
        search: Optional[str] = None
    ) -> Tuple[List[ElementGeneration], int]:
        """
        List generations accessible to a user with filtering and pagination.
        
        Args:
            user_id: ID of the requesting user
            page: Page number (1-based)
            page_size: Number of items per page
            project_id: Filter by project ID
            element_id: Filter by element ID
            execution_id: Filter by execution ID
            status: Filter by generation status
            search: Search in generation prompts and content
            
        Returns:
            Tuple[List[ElementGeneration], int]: List of generations and total count
        """
        try:
            # Build query conditions
            conditions = [ElementGeneration.is_deleted == False]
            
            # Get accessible project IDs
            if project_id:
                # Check specific project access
                project = await Project.get(PydanticObjectId(project_id))
                if not project or not project.is_accessible_by(user_id):
                    return [], 0
                conditions.append(ElementGeneration.project_id == project_id)
            else:
                # Get all accessible projects
                accessible_projects = await self._get_accessible_project_ids(user_id)
                if not accessible_projects:
                    return [], 0
                conditions.append(In(ElementGeneration.project_id, accessible_projects))
            
            # Apply filters
            if element_id:
                conditions.append(ElementGeneration.element_id == element_id)
            
            if execution_id:
                conditions.append(ElementGeneration.metadata["execution_id"] == execution_id)
            
            if status:
                conditions.append(ElementGeneration.status == status)
            
            if search:
                search_conditions = [
                    ElementGeneration.prompt.contains(search, case_insensitive=True)
                ]
                # Also search in chunks content if needed
                conditions.append(Or(*search_conditions))
            
            # Build final query
            query = ElementGeneration.find(And(*conditions))
            
            # Get total count
            total_count = await query.count()
            
            # Apply pagination and sorting
            generations = await query.sort(-ElementGeneration.updated_at).skip((page - 1) * page_size).limit(page_size).to_list()
            
            return generations, total_count
            
        except Exception as e:
            logger.error(f"Failed to list generations for user {user_id}: {str(e)}")
            return [], 0
    
    async def update_generation_status(
        self,
        generation_id: str,
        status: GenerationStatus,
        user_id: str,
        error_message: Optional[str] = None
    ) -> Optional[ElementGeneration]:
        """
        Update generation status.
        
        Args:
            generation_id: Generation ID to update
            status: New status
            user_id: ID of the requesting user
            error_message: Optional error message if status is FAILED
            
        Returns:
            ElementGeneration: Updated generation instance if successful, None otherwise
        """
        try:
            generation = await self.get_generation(generation_id, user_id)
            
            if not generation:
                return None
            
            # Update status
            generation.status = status
            
            if error_message:
                generation.error_message = error_message
            
            if status == GenerationStatus.COMPLETED:
                generation.completed_at = datetime.utcnow()
            
            # Update timestamp
            generation.update_timestamp()
            
            # Save changes
            await generation.save()
            
            logger.info(f"Updated generation {generation_id} status to {status}")
            return generation
            
        except Exception as e:
            logger.error(f"Failed to update generation status {generation_id}: {str(e)}")
            return None
    
    async def add_generation_chunk(
        self,
        generation_id: str,
        content: str,
        chunk_index: int,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Add a chunk to a generation.
        
        Args:
            generation_id: Generation ID
            content: Chunk content
            chunk_index: Index of the chunk
            metadata: Optional metadata for the chunk
            user_id: ID of the requesting user (optional for system updates)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            generation = await ElementGeneration.get(PydanticObjectId(generation_id))
            
            if not generation or generation.is_deleted:
                return False
            
            # If user_id provided, check access
            if user_id:
                project = await Project.get(PydanticObjectId(generation.project_id))
                if not project or not project.is_accessible_by(user_id):
                    return False
            
            # Create chunk
            chunk = GenerationChunk(
                content=content,
                chunk_index=chunk_index,
                metadata=metadata or {}
            )
            
            # Add chunk to generation
            generation.add_chunk(chunk)
            
            # Update timestamp
            generation.update_timestamp()
            
            # Save changes
            await generation.save()
            
            logger.info(f"Added chunk {chunk_index} to generation {generation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add chunk to generation {generation_id}: {str(e)}")
            return False
    
    async def update_generation_metrics(
        self,
        generation_id: str,
        metrics: GenerationMetrics,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Update generation metrics.
        
        Args:
            generation_id: Generation ID
            metrics: Updated metrics
            user_id: ID of the requesting user (optional for system updates)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            generation = await ElementGeneration.get(PydanticObjectId(generation_id))
            
            if not generation or generation.is_deleted:
                return False
            
            # If user_id provided, check access
            if user_id:
                project = await Project.get(PydanticObjectId(generation.project_id))
                if not project or not project.is_accessible_by(user_id):
                    return False
            
            # Update metrics
            generation.metrics = metrics
            
            # Update timestamp
            generation.update_timestamp()
            
            # Save changes
            await generation.save()
            
            logger.info(f"Updated metrics for generation {generation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metrics for generation {generation_id}: {str(e)}")
            return False
    
    async def delete_generation(self, generation_id: str, user_id: str) -> bool:
        """
        Delete a generation (soft delete) with access control.
        
        Args:
            generation_id: Generation ID to delete
            user_id: ID of the requesting user
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            generation = await ElementGeneration.get(PydanticObjectId(generation_id))
            
            if not generation or generation.is_deleted:
                return False
            
            # Check project access
            project = await Project.get(PydanticObjectId(generation.project_id))
            if not project or not project.is_accessible_by(user_id):
                return False
            
            # Only creator or project owner can delete
            if generation.created_by != user_id and project.owner_id != user_id:
                return False
            
            # Perform soft delete
            generation.mark_deleted()
            await generation.save()
            
            # Remove from element and project
            element = await Element.get(PydanticObjectId(generation.element_id))
            if element:
                element.remove_generation(generation_id)
                await element.save()
            
            project.remove_generation(generation_id)
            await project.save()
            
            logger.info(f"Deleted generation {generation_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete generation {generation_id}: {str(e)}")
            return False
    
    async def get_generation_statistics(
        self,
        generation_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get generation statistics and analytics.
        
        Args:
            generation_id: Generation ID
            user_id: ID of the requesting user
            
        Returns:
            Dict[str, Any]: Generation statistics if accessible, None otherwise
        """
        try:
            generation = await self.get_generation(generation_id, user_id)
            
            if not generation:
                return None
            
            element = await Element.get(PydanticObjectId(generation.element_id))
            full_content = generation.get_full_content()
            
            return {
                "id": str(generation.id),
                "element_id": generation.element_id,
                "project_id": generation.project_id,
                "element_name": element.name if element else "Unknown Element",
                "status": generation.status.value,
                "model_used": generation.model_used,
                "prompt": generation.template.generation_prompt if generation.template else "",
                "output_text": full_content,
                "tokens_used": generation.metrics.total_tokens if generation.metrics else 0,
                "execution_time": generation.metrics.generation_time_ms / 1000 if generation.metrics and generation.metrics.generation_time_ms else 0,
                "cost_usd": generation.metrics.estimated_cost if generation.metrics and generation.metrics.estimated_cost else 0.0,
                "created_at": generation.created_at.isoformat(),
                "updated_at": generation.updated_at.isoformat(),
                "error_message": generation.error_details.get("error") if generation.error_details else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get generation statistics {generation_id}: {str(e)}")
            return None
    
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