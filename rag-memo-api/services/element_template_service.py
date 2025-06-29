"""
Element Template Service for TinyRAG v1.4.

This service manages element templates and handles automatic provisioning
of templates to projects when they are created.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId

from models.element_template import ElementTemplate
from models.element import Element, ElementContent
from models.project import Project
from models.tenant_configuration import TenantConfiguration
from models.enums import TenantType, ElementStatus
from services.prompt_summarization_service import get_summarization_service


class ElementTemplateService:
    """
    Service for managing element templates and automatic provisioning.
    
    This service provides functionality to:
    - Create and manage element templates
    - Automatically provision templates to new projects
    - Track template usage and performance
    - Generate retrieval prompts for templates
    """
    
    def __init__(self):
        """Initialize the element template service."""
        self.logger = logging.getLogger(__name__)
        self.summarization_service = get_summarization_service()
    
    async def create_template(
        self,
        template_data: Dict[str, Any],
        created_by: str,
        generate_retrieval_prompt: bool = True
    ) -> ElementTemplate:
        """
        Create a new element template.
        
        Args:
            template_data: Template data dictionary
            created_by: User ID of template creator
            generate_retrieval_prompt: Whether to auto-generate retrieval prompt
            
        Returns:
            Created element template
        """
        # Validate required fields
        required_fields = ['name', 'description', 'tenant_type', 'task_type', 'element_type', 'generation_prompt']
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Required field missing: {field}")
        
        # Check for duplicate template name within tenant
        existing = await ElementTemplate.find_one({
            "name": template_data['name'],
            "tenant_type": template_data['tenant_type']
        })
        if existing:
            raise ValueError(f"Template with name '{template_data['name']}' already exists for tenant {template_data['tenant_type']}")
        
        # Create template
        template = ElementTemplate(
            **template_data,
            created_by=created_by,
            is_system_default=template_data.get('is_system_default', True)
        )
        
        # Generate retrieval prompt if requested
        if generate_retrieval_prompt and template.generation_prompt:
            try:
                context = {
                    'tenant_type': template.tenant_type,
                    'element_type': template.element_type,
                    'template_name': template.name
                }
                
                retrieval_prompt = await self.summarization_service.summarize_prompt(
                    generation_prompt=template.generation_prompt,
                    context=context
                )
                template.retrieval_prompt = retrieval_prompt
                self.logger.info(f"Generated retrieval prompt for template: {template.name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to generate retrieval prompt: {e}")
        
        # Save template
        await template.insert()
        
        # Update tenant template count
        await self._update_tenant_template_count(template.tenant_type)
        
        self.logger.info(f"Created template: {template.name} for tenant {template.tenant_type}")
        
        return template
    
    async def get_templates_by_tenant(
        self,
        tenant_type: TenantType,
        active_only: bool = True
    ) -> List[ElementTemplate]:
        """
        Get all templates for a specific tenant type.
        
        Args:
            tenant_type: Tenant type to filter by
            active_only: Whether to return only active templates
            
        Returns:
            List of element templates
        """
        query = {"tenant_type": tenant_type}
        if active_only:
            query["status"] = ElementStatus.ACTIVE
        
        templates = await ElementTemplate.find(query).sort("name").to_list()
        return templates
    
    async def provision_templates_to_project(
        self,
        project_id: str,
        tenant_type: TenantType,
        batch_id: Optional[str] = None,
        force: bool = False
    ) -> List[Element]:
        """
        Provision all active templates to a project.
        
        Args:
            project_id: Project ID to provision templates to
            tenant_type: Tenant type of the project
            batch_id: Optional batch ID for tracking
            force: Whether to replace existing elements
            
        Returns:
            List of created elements
        """
        # Validate project exists
        project = await Project.get(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        # Check tenant compatibility
        if project.tenant_type != tenant_type:
            self.logger.warning(
                f"Project tenant type ({project.tenant_type}) "
                f"doesn't match requested tenant type ({tenant_type})"
            )
        
        # Get active templates for tenant
        templates = await self.get_templates_by_tenant(tenant_type, active_only=True)
        
        if not templates:
            self.logger.info(f"No active templates found for tenant: {tenant_type}")
            return []
        
        # Check if project already has default elements
        if not force:
            existing_default_count = await Element.find({
                "project_id": project_id,
                "is_default_element": True
            }).count()
            
            if existing_default_count > 0:
                self.logger.info(
                    f"Project {project_id} already has {existing_default_count} default elements. "
                    "Use force=True to replace them."
                )
                return []
        
        # Generate batch ID if not provided
        if batch_id is None:
            batch_id = f"provision_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        created_elements = []
        
        for template in templates:
            try:
                # Create element from template
                element = await self._create_element_from_template(
                    template=template,
                    project_id=project_id,
                    owner_id=project.owner_id,
                    batch_id=batch_id
                )
                
                created_elements.append(element)
                
                # Update template usage
                template.increment_usage()
                template.increment_element_count()
                await template.save()
                
            except Exception as e:
                self.logger.error(f"Failed to create element from template {template.id}: {e}")
        
        self.logger.info(
            f"Provisioned {len(created_elements)} elements to project {project_id} "
            f"from {len(templates)} templates"
        )
        
        return created_elements
    
    async def _create_element_from_template(
        self,
        template: ElementTemplate,
        project_id: str,
        owner_id: str,
        batch_id: str
    ) -> Element:
        """Create an element from a template."""
        # Create element content
        element_content = ElementContent(
            content=template.generation_prompt,  # Legacy field
            generation_prompt=template.generation_prompt,
            retrieval_prompt=template.retrieval_prompt,
            variables=template.variables.copy(),
            execution_config=template.execution_config.copy(),
            version=template.version,
            changelog=template.changelog.copy()
        )
        
        # Create element
        element = Element(
            name=template.name,
            description=template.description,
            project_id=project_id,
            tenant_type=template.tenant_type,
            task_type=template.task_type,
            element_type=template.element_type,
            status=ElementStatus.ACTIVE,
            template=element_content,
            tags=template.tags.copy(),
            owner_id=owner_id,
            is_default_element=True,
            template_id=str(template.id),
            insertion_batch_id=batch_id
        )
        
        await element.insert()
        return element
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any],
        updated_by: str
    ) -> ElementTemplate:
        """
        Update an existing template.
        
        Args:
            template_id: Template ID to update
            updates: Update data dictionary
            updated_by: User ID making the update
            
        Returns:
            Updated template
        """
        template = await ElementTemplate.get(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Handle version update
        if 'version' in updates:
            changelog_entry = updates.pop('changelog_entry', 'Template updated')
            template.update_version(updates['version'], changelog_entry)
        
        # Update fields
        for field, value in updates.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        # Regenerate retrieval prompt if generation prompt changed
        if 'generation_prompt' in updates and template.generation_prompt:
            try:
                context = {
                    'tenant_type': template.tenant_type,
                    'element_type': template.element_type,
                    'template_name': template.name
                }
                
                retrieval_prompt = await self.summarization_service.summarize_prompt(
                    generation_prompt=template.generation_prompt,
                    context=context
                )
                template.retrieval_prompt = retrieval_prompt
                self.logger.info(f"Regenerated retrieval prompt for template: {template.name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to regenerate retrieval prompt: {e}")
        
        await template.save()
        
        self.logger.info(f"Updated template: {template_id}")
        
        return template
    
    async def delete_template(self, template_id: str) -> bool:
        """
        Delete a template (soft delete by default).
        
        Args:
            template_id: Template ID to delete
            
        Returns:
            True if deleted successfully
        """
        template = await ElementTemplate.get(template_id)
        if not template:
            return False
        
        # Check if template is in use
        elements_using_template = await Element.find({
            "template_id": template_id
        }).count()
        
        if elements_using_template > 0:
            # Soft delete - mark as inactive
            template.status = ElementStatus.INACTIVE
            await template.save()
            self.logger.info(f"Soft deleted template {template_id} (has {elements_using_template} elements)")
        else:
            # Hard delete if no elements use it
            await template.delete()
            self.logger.info(f"Hard deleted template {template_id}")
        
        # Update tenant template count
        await self._update_tenant_template_count(template.tenant_type)
        
        return True
    
    async def get_template_usage_stats(self, template_id: str) -> Dict[str, Any]:
        """Get usage statistics for a template."""
        template = await ElementTemplate.get(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Count elements created from this template
        element_count = await Element.find({
            "template_id": template_id
        }).count()
        
        # Get project distribution
        elements = await Element.find({
            "template_id": template_id
        }).to_list()
        
        project_ids = list(set(elem.project_id for elem in elements))
        projects = await Project.find({
            "_id": {"$in": [ObjectId(pid) for pid in project_ids]}
        }).to_list()
        
        return {
            "template_id": template_id,
            "template_name": template.name,
            "usage_count": template.usage_count,
            "element_count": element_count,
            "project_count": len(projects),
            "success_rate": template.success_rate,
            "last_used_at": template.last_used_at.isoformat() if template.last_used_at else None,
            "projects": [
                {
                    "id": str(project.id),
                    "name": project.name,
                    "tenant_type": project.tenant_type.value
                }
                for project in projects
            ]
        }
    
    async def regenerate_all_retrieval_prompts(
        self,
        tenant_type: Optional[TenantType] = None,
        template_ids: Optional[List[str]] = None
    ) -> Tuple[int, int]:
        """
        Regenerate retrieval prompts for templates.
        
        Args:
            tenant_type: Filter by tenant type
            template_ids: Specific template IDs to process
            
        Returns:
            Tuple of (processed_count, success_count)
        """
        # Build query
        query = {}
        if tenant_type:
            query["tenant_type"] = tenant_type
        if template_ids:
            query["_id"] = {"$in": [ObjectId(tid) for tid in template_ids]}
        
        templates = await ElementTemplate.find(query).to_list()
        
        if not templates:
            return 0, 0
        
        success_count = 0
        
        for template in templates:
            if not template.generation_prompt:
                continue
            
            try:
                context = {
                    'tenant_type': template.tenant_type,
                    'element_type': template.element_type,
                    'template_name': template.name
                }
                
                retrieval_prompt = await self.summarization_service.summarize_prompt(
                    generation_prompt=template.generation_prompt,
                    context=context
                )
                
                template.retrieval_prompt = retrieval_prompt
                await template.save()
                success_count += 1
                
                self.logger.info(f"Regenerated retrieval prompt for template: {template.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to regenerate prompt for template {template.id}: {e}")
        
        return len(templates), success_count
    
    async def _update_tenant_template_count(self, tenant_type: TenantType) -> None:
        """Update the template count for a tenant configuration."""
        try:
            template_count = await ElementTemplate.find({
                "tenant_type": tenant_type,
                "status": ElementStatus.ACTIVE
            }).count()
            
            tenant_config = await TenantConfiguration.get_by_tenant_type(tenant_type)
            if tenant_config:
                tenant_config.update_template_count(template_count)
                await tenant_config.save()
                
        except Exception as e:
            self.logger.error(f"Failed to update tenant template count: {e}")
    
    async def cleanup_unused_templates(
        self,
        older_than_days: int = 90,
        dry_run: bool = True
    ) -> Tuple[int, List[str]]:
        """
        Clean up unused templates older than specified days.
        
        Args:
            older_than_days: Templates older than this will be considered for cleanup
            dry_run: If True, only return what would be deleted
            
        Returns:
            Tuple of (count, template_ids)
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        # Find templates that are:
        # 1. Older than cutoff date
        # 2. Have usage_count == 0 or no recent usage
        # 3. Are not currently used by any elements
        query = {
            "created_at": {"$lt": cutoff_date},
            "$or": [
                {"usage_count": 0},
                {"last_used_at": {"$lt": cutoff_date}},
                {"last_used_at": None}
            ]
        }
        
        templates = await ElementTemplate.find(query).to_list()
        unused_templates = []
        
        for template in templates:
            # Check if template is actually unused
            element_count = await Element.find({
                "template_id": str(template.id)
            }).count()
            
            if element_count == 0:
                unused_templates.append(template)
        
        template_ids = [str(t.id) for t in unused_templates]
        
        if not dry_run and unused_templates:
            for template in unused_templates:
                await template.delete()
            
            self.logger.info(f"Cleaned up {len(unused_templates)} unused templates")
        
        return len(unused_templates), template_ids


# Global service instance
_template_service = None


def get_template_service() -> ElementTemplateService:
    """Get the global element template service instance."""
    global _template_service
    
    if _template_service is None:
        _template_service = ElementTemplateService()
    
    return _template_service 