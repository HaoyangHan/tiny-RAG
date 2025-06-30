#!/usr/bin/env python3
"""
Provision Project - TinyRAG v1.4

This script provisions element templates to existing projects,
enabling automatic setup of default elements.
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Element, ElementTemplate, Project, TenantConfiguration
from models.enums import TenantType
from services.element_template_service import get_template_service
from database import get_database_url


class ProjectProvisioner:
    """Service for provisioning templates to projects."""
    
    def __init__(self):
        """Initialize the project provisioner."""
        self.logger = logging.getLogger(__name__)
        self.template_service = get_template_service()
    
    async def provision_project(
        self,
        project_id: str,
        tenant_type: Optional[TenantType] = None,
        template_ids: Optional[List[str]] = None,
        prefix: str = "",
        dry_run: bool = True,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Provision templates to a specific project.
        
        Args:
            project_id: Project ID to provision
            tenant_type: Override tenant type (uses project's tenant if None)
            template_ids: Specific template IDs to provision
            prefix: Prefix for element names
            dry_run: Show what would be created
            force: Replace existing default elements
            
        Returns:
            Provisioning report
        """
        self.logger.info(f"🎯 Provisioning project: {project_id}")
        
        # Validate project exists
        project = await Project.get(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        # Determine tenant type
        target_tenant = tenant_type or project.tenant_type
        
        self.logger.info(f"📊 Project details:")
        self.logger.info(f"   • Name: {project.name}")
        self.logger.info(f"   • Tenant: {project.tenant_type.value}")
        self.logger.info(f"   • Target tenant: {target_tenant.value}")
        self.logger.info(f"   • Owner: {project.owner_id}")
        
        # Check existing elements
        existing_elements = await Element.find({
            "project_id": project_id,
            "is_default_element": True
        }).to_list()
        
        if existing_elements and not force:
            self.logger.warning(f"⚠️  Project has {len(existing_elements)} default elements")
            if not dry_run:
                confirm = input("Replace existing default elements? (y/N): ")
                if confirm.lower() != 'y':
                    return {
                        "status": "cancelled",
                        "message": "User cancelled due to existing elements"
                    }
        
        # Get templates to provision
        if template_ids:
            templates = []
            for template_id in template_ids:
                template = await ElementTemplate.get(template_id)
                if template:
                    templates.append(template)
                else:
                    self.logger.warning(f"⚠️  Template not found: {template_id}")
        else:
            templates = await self.template_service.get_templates_by_tenant(
                tenant_type=target_tenant,
                active_only=True
            )
        
        if not templates:
            self.logger.info(f"✅ No templates found for tenant: {target_tenant.value}")
            return {
                "status": "no_templates",
                "message": f"No templates available for {target_tenant.value}"
            }
        
        self.logger.info(f"📝 Found {len(templates)} templates to provision:")
        for template in templates:
            self.logger.info(f"   • {template.name} ({template.element_type.value})")
        
        if dry_run:
            return await self._simulate_provisioning(
                project=project,
                templates=templates,
                prefix=prefix,
                existing_elements=existing_elements
            )
        else:
            return await self._perform_provisioning(
                project=project,
                templates=templates,
                prefix=prefix,
                force=force
            )
    
    async def _simulate_provisioning(
        self,
        project: Project,
        templates: List[ElementTemplate],
        prefix: str,
        existing_elements: List[Element]
    ) -> Dict[str, Any]:
        """Simulate provisioning and show what would be created."""
        would_create = []
        
        for template in templates:
            element_name = f"{prefix}{template.name}" if prefix else template.name
            would_create.append({
                "name": element_name,
                "template_name": template.name,
                "element_type": template.element_type.value,
                "template_id": str(template.id)
            })
        
        return {
            "status": "dry_run",
            "project_id": str(project.id),
            "project_name": project.name,
            "tenant_type": project.tenant_type.value,
            "existing_elements": len(existing_elements),
            "would_create": len(would_create),
            "elements": would_create
        }
    
    async def _perform_provisioning(
        self,
        project: Project,
        templates: List[ElementTemplate],
        prefix: str,
        force: bool
    ) -> Dict[str, Any]:
        """Perform actual provisioning."""
        batch_id = f"provision_{project.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Remove existing default elements if force
        if force:
            existing_count = await self._remove_existing_default_elements(project.id)
            self.logger.info(f"🗑️  Removed {existing_count} existing default elements")
        
        # Provision templates
        created_elements = await self.template_service.provision_templates_to_project(
            project_id=str(project.id),
            tenant_type=project.tenant_type,
            batch_id=batch_id,
            force=force
        )
        
        # Apply prefix if specified
        if prefix:
            for element in created_elements:
                element.name = f"{prefix}{element.name}"
                await element.save()
        
        self.logger.info(f"✅ Provisioned {len(created_elements)} elements to project")
        
        return {
            "status": "completed",
            "project_id": str(project.id),
            "project_name": project.name,
            "tenant_type": project.tenant_type.value,
            "batch_id": batch_id,
            "created_count": len(created_elements),
            "elements": [
                {
                    "id": str(elem.id),
                    "name": elem.name,
                    "element_type": elem.element_type.value,
                    "template_id": elem.template_id
                }
                for elem in created_elements
            ]
        }
    
    async def _remove_existing_default_elements(self, project_id: str) -> int:
        """Remove existing default elements from project."""
        elements = await Element.find({
            "project_id": project_id,
            "is_default_element": True
        }).to_list()
        
        for element in elements:
            await element.delete()
        
        return len(elements)
    
    async def provision_multiple_projects(
        self,
        project_ids: List[str],
        dry_run: bool = True,
        force: bool = False
    ) -> Dict[str, Any]:
        """Provision templates to multiple projects."""
        self.logger.info(f"🚀 Provisioning {len(project_ids)} projects...")
        
        results = {}
        total_created = 0
        total_errors = 0
        
        for project_id in project_ids:
            try:
                result = await self.provision_project(
                    project_id=project_id,
                    dry_run=dry_run,
                    force=force
                )
                results[project_id] = result
                
                if result.get("status") == "completed":
                    total_created += result.get("created_count", 0)
                
            except Exception as e:
                self.logger.error(f"❌ Failed to provision project {project_id}: {e}")
                results[project_id] = {"error": str(e)}
                total_errors += 1
        
        return {
            "operation": "provision_multiple",
            "total_projects": len(project_ids),
            "total_created": total_created,
            "total_errors": total_errors,
            "results": results
        }


async def main():
    """Main function to run the project provisioner."""
    parser = argparse.ArgumentParser(
        description="Provision element templates to projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run for single project
  python provision_project.py --project-id 507f1f77bcf86cd799439012 --dry-run

  # Provision all templates to project
  python provision_project.py --project-id 507f1f77bcf86cd799439012

  # Provision specific templates
  python provision_project.py --project-id 507f1f77bcf86cd799439012 --template-ids id1,id2

  # Provision with custom prefix
  python provision_project.py --project-id 507f1f77bcf86cd799439012 --prefix "Custom_"

  # Force replace existing elements
  python provision_project.py --project-id 507f1f77bcf86cd799439012 --force
        """
    )
    
    parser.add_argument(
        "--project-id",
        type=str,
        required=True,
        help="Project ID to provision templates to"
    )
    
    parser.add_argument(
        "--tenant",
        type=str,
        choices=[t.value for t in TenantType],
        help="Override tenant type (uses project's tenant if not specified)"
    )
    
    parser.add_argument(
        "--template-ids",
        type=str,
        help="Comma-separated list of specific template IDs to provision"
    )
    
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Prefix for element names"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing default elements"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize database
        logger.info("🔌 Connecting to database...")
        client = AsyncIOMotorClient(get_database_url())
        await init_beanie(
            database=client.tinyrag,
            document_models=[Element, ElementTemplate, Project, TenantConfiguration]
        )
        logger.info("✅ Database connected successfully")
        
        # Initialize provisioner
        provisioner = ProjectProvisioner()
        
        # Parse template IDs if provided
        template_ids = None
        if args.template_ids:
            template_ids = [tid.strip() for tid in args.template_ids.split(',')]
        
        # Parse tenant type if provided
        tenant_type = None
        if args.tenant:
            tenant_type = TenantType(args.tenant)
        
        # Execute provisioning
        report = await provisioner.provision_project(
            project_id=args.project_id,
            tenant_type=tenant_type,
            template_ids=template_ids,
            prefix=args.prefix,
            dry_run=args.dry_run,
            force=args.force
        )
        
        print(f"\n✅ Provisioning complete: {report}")
        
    except KeyboardInterrupt:
        logger.info("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    asyncio.run(main()) 