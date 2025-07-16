#!/usr/bin/env python3
"""
Remove Script Elements - TinyRAG v1.4

This script removes elements that were inserted by previous scripts,
with safety features and comprehensive tracking.
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Element, ElementTemplate, TenantConfiguration
from models.enums import TenantType
from database import get_database_url


class ScriptElementRemover:
    """
    Service for removing elements inserted by scripts.
    
    Provides safe removal of script-inserted elements with tracking,
    dry-run capabilities, and comprehensive reporting.
    """
    
    def __init__(self):
        """Initialize the script element remover."""
        self.logger = logging.getLogger(__name__)
        self.removed_count = 0
        self.error_count = 0
        self.processed_batches: List[str] = []
        self.removal_report: Dict[str, Any] = {}
    
    async def remove_all_script_elements(
        self,
        dry_run: bool = True,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Remove all elements inserted by scripts.
        
        Args:
            dry_run: If True, only show what would be removed
            force: If True, bypass confirmation prompts
            
        Returns:
            Removal report with statistics
        """
        self.logger.info("🔍 Finding all script-inserted elements...")
        
        # Find all elements with insertion_batch_id (script-inserted)
        script_elements = await Element.find({
            "insertion_batch_id": {"$exists": True, "$ne": None}
        }).to_list()
        
        if not script_elements:
            self.logger.info("✅ No script-inserted elements found")
            return {"removed_count": 0, "message": "No elements to remove"}
        
        # Group by batch ID and tenant
        batch_groups = {}
        tenant_groups = {}
        
        for element in script_elements:
            # Group by batch
            batch_id = element.insertion_batch_id
            if batch_id not in batch_groups:
                batch_groups[batch_id] = []
            batch_groups[batch_id].append(element)
            
            # Group by tenant
            tenant = element.tenant_type.value
            if tenant not in tenant_groups:
                tenant_groups[tenant] = []
            tenant_groups[tenant].append(element)
        
        self.logger.info(f"📊 Found {len(script_elements)} script-inserted elements:")
        self.logger.info(f"   • {len(batch_groups)} insertion batches")
        self.logger.info(f"   • {len(tenant_groups)} tenant types")
        
        for batch_id, elements in batch_groups.items():
            self.logger.info(f"   • Batch '{batch_id}': {len(elements)} elements")
        
        for tenant, elements in tenant_groups.items():
            self.logger.info(f"   • Tenant '{tenant}': {len(elements)} elements")
        
        # Confirmation
        if not force and not dry_run:
            confirm = input(f"\n⚠️  Remove {len(script_elements)} script-inserted elements? (y/N): ")
            if confirm.lower() != 'y':
                self.logger.info("❌ Removal cancelled by user")
                return {"removed_count": 0, "message": "Cancelled by user"}
        
        # Remove elements
        if dry_run:
            self.logger.info("🧪 DRY RUN - No elements will be actually removed")
            return await self._simulate_removal(script_elements, batch_groups, tenant_groups)
        else:
            self.logger.info("🗑️  Removing script-inserted elements...")
            return await self._perform_removal(script_elements, batch_groups, tenant_groups)
    
    async def remove_by_tenant(
        self,
        tenant_type: TenantType,
        dry_run: bool = True,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Remove script-inserted elements for a specific tenant.
        
        Args:
            tenant_type: Tenant type to filter by
            dry_run: If True, only show what would be removed
            force: If True, bypass confirmation prompts
            
        Returns:
            Removal report
        """
        self.logger.info(f"🔍 Finding script-inserted elements for tenant: {tenant_type.value}")
        
        elements = await Element.find({
            "tenant_type": tenant_type,
            "insertion_batch_id": {"$exists": True, "$ne": None}
        }).to_list()
        
        if not elements:
            self.logger.info(f"✅ No script-inserted elements found for tenant: {tenant_type.value}")
            return {"removed_count": 0, "message": f"No elements found for tenant {tenant_type.value}"}
        
        self.logger.info(f"📊 Found {len(elements)} script-inserted elements for tenant {tenant_type.value}")
        
        # Confirmation
        if not force and not dry_run:
            confirm = input(f"\n⚠️  Remove {len(elements)} elements for tenant {tenant_type.value}? (y/N): ")
            if confirm.lower() != 'y':
                self.logger.info("❌ Removal cancelled by user")
                return {"removed_count": 0, "message": "Cancelled by user"}
        
        if dry_run:
            self.logger.info("🧪 DRY RUN - No elements will be actually removed")
            return await self._simulate_tenant_removal(elements, tenant_type)
        else:
            self.logger.info(f"🗑️  Removing elements for tenant: {tenant_type.value}")
            return await self._perform_tenant_removal(elements, tenant_type)
    
    async def remove_by_batch(
        self,
        batch_id: str,
        dry_run: bool = True,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Remove elements from a specific insertion batch.
        
        Args:
            batch_id: Batch ID to remove
            dry_run: If True, only show what would be removed
            force: If True, bypass confirmation prompts
            
        Returns:
            Removal report
        """
        self.logger.info(f"🔍 Finding elements from batch: {batch_id}")
        
        elements = await Element.find({
            "insertion_batch_id": batch_id
        }).to_list()
        
        if not elements:
            self.logger.info(f"✅ No elements found for batch: {batch_id}")
            return {"removed_count": 0, "message": f"No elements found for batch {batch_id}"}
        
        self.logger.info(f"📊 Found {len(elements)} elements in batch: {batch_id}")
        
        # Show batch details
        tenant_distribution = {}
        for element in elements:
            tenant = element.tenant_type.value
            tenant_distribution[tenant] = tenant_distribution.get(tenant, 0) + 1
        
        for tenant, count in tenant_distribution.items():
            self.logger.info(f"   • {tenant}: {count} elements")
        
        # Confirmation
        if not force and not dry_run:
            confirm = input(f"\n⚠️  Remove {len(elements)} elements from batch {batch_id}? (y/N): ")
            if confirm.lower() != 'y':
                self.logger.info("❌ Removal cancelled by user")
                return {"removed_count": 0, "message": "Cancelled by user"}
        
        if dry_run:
            self.logger.info("🧪 DRY RUN - No elements will be actually removed")
            return await self._simulate_batch_removal(elements, batch_id)
        else:
            self.logger.info(f"🗑️  Removing elements from batch: {batch_id}")
            return await self._perform_batch_removal(elements, batch_id)
    
    async def remove_by_project(
        self,
        project_id: str,
        default_only: bool = True,
        dry_run: bool = True,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Remove script-inserted elements from a specific project.
        
        Args:
            project_id: Project ID to clean up
            default_only: If True, only remove default elements
            dry_run: If True, only show what would be removed
            force: If True, bypass confirmation prompts
            
        Returns:
            Removal report
        """
        self.logger.info(f"🔍 Finding script-inserted elements in project: {project_id}")
        
        query = {"project_id": project_id}
        if default_only:
            query["is_default_element"] = True
        else:
            query["insertion_batch_id"] = {"$exists": True, "$ne": None}
        
        elements = await Element.find(query).to_list()
        
        if not elements:
            element_type = "default" if default_only else "script-inserted"
            self.logger.info(f"✅ No {element_type} elements found in project: {project_id}")
            return {"removed_count": 0, "message": f"No {element_type} elements found in project"}
        
        element_type = "default" if default_only else "script-inserted"
        self.logger.info(f"📊 Found {len(elements)} {element_type} elements in project: {project_id}")
        
        # Confirmation
        if not force and not dry_run:
            confirm = input(f"\n⚠️  Remove {len(elements)} {element_type} elements from project? (y/N): ")
            if confirm.lower() != 'y':
                self.logger.info("❌ Removal cancelled by user")
                return {"removed_count": 0, "message": "Cancelled by user"}
        
        if dry_run:
            self.logger.info("🧪 DRY RUN - No elements will be actually removed")
            return await self._simulate_project_removal(elements, project_id, default_only)
        else:
            self.logger.info(f"🗑️  Removing {element_type} elements from project: {project_id}")
            return await self._perform_project_removal(elements, project_id, default_only)
    
    async def _simulate_removal(
        self,
        elements: List[Element],
        batch_groups: Dict[str, List[Element]],
        tenant_groups: Dict[str, List[Element]]
    ) -> Dict[str, Any]:
        """Simulate removal and return what would be removed."""
        report = {
            "operation": "dry_run",
            "total_elements": len(elements),
            "would_remove": len(elements),
            "batch_distribution": {
                batch_id: len(batch_elements)
                for batch_id, batch_elements in batch_groups.items()
            },
            "tenant_distribution": {
                tenant: len(tenant_elements)
                for tenant, tenant_elements in tenant_groups.items()
            },
            "elements": [
                {
                    "id": str(element.id),
                    "name": element.name,
                    "tenant": element.tenant_type.value,
                    "batch_id": element.insertion_batch_id,
                    "project_id": element.project_id
                }
                for element in elements
            ]
        }
        
        self.logger.info(f"✅ DRY RUN COMPLETE: Would remove {len(elements)} elements")
        return report
    
    async def _perform_removal(
        self,
        elements: List[Element],
        batch_groups: Dict[str, List[Element]],
        tenant_groups: Dict[str, List[Element]]
    ) -> Dict[str, Any]:
        """Perform actual removal of elements."""
        removed_elements = []
        failed_elements = []
        
        for element in elements:
            try:
                await element.delete()
                removed_elements.append(element)
                self.logger.debug(f"✅ Removed element: {element.name} ({element.id})")
            except Exception as e:
                failed_elements.append({"element": element, "error": str(e)})
                self.logger.error(f"❌ Failed to remove element {element.name}: {e}")
        
        # Update tenant statistics
        await self._update_tenant_statistics(tenant_groups.keys())
        
        report = {
            "operation": "removal",
            "total_elements": len(elements),
            "removed_count": len(removed_elements),
            "failed_count": len(failed_elements),
            "batch_distribution": {
                batch_id: len(batch_elements)
                for batch_id, batch_elements in batch_groups.items()
            },
            "tenant_distribution": {
                tenant: len(tenant_elements)
                for tenant, tenant_elements in tenant_groups.items()
            },
            "failed_elements": [
                {
                    "id": str(item["element"].id),
                    "name": item["element"].name,
                    "error": item["error"]
                }
                for item in failed_elements
            ]
        }
        
        self.logger.info(f"✅ REMOVAL COMPLETE: Removed {len(removed_elements)} elements")
        if failed_elements:
            self.logger.warning(f"⚠️  {len(failed_elements)} elements failed to remove")
        
        return report
    
    async def _simulate_tenant_removal(
        self,
        elements: List[Element],
        tenant_type: TenantType
    ) -> Dict[str, Any]:
        """Simulate tenant-specific removal."""
        batch_distribution = {}
        for element in elements:
            batch_id = element.insertion_batch_id
            batch_distribution[batch_id] = batch_distribution.get(batch_id, 0) + 1
        
        return {
            "operation": "dry_run_tenant",
            "tenant_type": tenant_type.value,
            "total_elements": len(elements),
            "would_remove": len(elements),
            "batch_distribution": batch_distribution
        }
    
    async def _perform_tenant_removal(
        self,
        elements: List[Element],
        tenant_type: TenantType
    ) -> Dict[str, Any]:
        """Perform tenant-specific removal."""
        removed_count = 0
        failed_count = 0
        
        for element in elements:
            try:
                await element.delete()
                removed_count += 1
            except Exception as e:
                failed_count += 1
                self.logger.error(f"❌ Failed to remove element {element.name}: {e}")
        
        # Update tenant configuration
        tenant_config = await TenantConfiguration.get_by_tenant_type(tenant_type)
        if tenant_config:
            tenant_config.decrement_element_count(removed_count)
            await tenant_config.save()
        
        return {
            "operation": "tenant_removal",
            "tenant_type": tenant_type.value,
            "total_elements": len(elements),
            "removed_count": removed_count,
            "failed_count": failed_count
        }
    
    async def _simulate_batch_removal(
        self,
        elements: List[Element],
        batch_id: str
    ) -> Dict[str, Any]:
        """Simulate batch-specific removal."""
        tenant_distribution = {}
        for element in elements:
            tenant = element.tenant_type.value
            tenant_distribution[tenant] = tenant_distribution.get(tenant, 0) + 1
        
        return {
            "operation": "dry_run_batch",
            "batch_id": batch_id,
            "total_elements": len(elements),
            "would_remove": len(elements),
            "tenant_distribution": tenant_distribution
        }
    
    async def _perform_batch_removal(
        self,
        elements: List[Element],
        batch_id: str
    ) -> Dict[str, Any]:
        """Perform batch-specific removal."""
        removed_count = 0
        failed_count = 0
        tenant_counts = {}
        
        for element in elements:
            try:
                tenant = element.tenant_type
                tenant_counts[tenant] = tenant_counts.get(tenant, 0) + 1
                await element.delete()
                removed_count += 1
            except Exception as e:
                failed_count += 1
                self.logger.error(f"❌ Failed to remove element {element.name}: {e}")
        
        # Update tenant statistics
        for tenant_type, count in tenant_counts.items():
            tenant_config = await TenantConfiguration.get_by_tenant_type(tenant_type)
            if tenant_config:
                tenant_config.decrement_element_count(count)
                await tenant_config.save()
        
        return {
            "operation": "batch_removal",
            "batch_id": batch_id,
            "total_elements": len(elements),
            "removed_count": removed_count,
            "failed_count": failed_count,
            "tenant_distribution": {
                tenant.value: count for tenant, count in tenant_counts.items()
            }
        }
    
    async def _simulate_project_removal(
        self,
        elements: List[Element],
        project_id: str,
        default_only: bool
    ) -> Dict[str, Any]:
        """Simulate project-specific removal."""
        return {
            "operation": "dry_run_project",
            "project_id": project_id,
            "default_only": default_only,
            "total_elements": len(elements),
            "would_remove": len(elements)
        }
    
    async def _perform_project_removal(
        self,
        elements: List[Element],
        project_id: str,
        default_only: bool
    ) -> Dict[str, Any]:
        """Perform project-specific removal."""
        removed_count = 0
        failed_count = 0
        
        for element in elements:
            try:
                await element.delete()
                removed_count += 1
            except Exception as e:
                failed_count += 1
                self.logger.error(f"❌ Failed to remove element {element.name}: {e}")
        
        return {
            "operation": "project_removal",
            "project_id": project_id,
            "default_only": default_only,
            "total_elements": len(elements),
            "removed_count": removed_count,
            "failed_count": failed_count
        }
    
    async def _update_tenant_statistics(self, tenant_types: List[str]) -> None:
        """Update tenant configuration statistics after removal."""
        for tenant_name in tenant_types:
            try:
                tenant_type = TenantType(tenant_name)
                tenant_config = await TenantConfiguration.get_by_tenant_type(tenant_type)
                
                if tenant_config:
                    # Recount elements for this tenant
                    element_count = await Element.find({
                        "tenant_type": tenant_type
                    }).count()
                    
                    tenant_config.element_count = element_count
                    await tenant_config.save()
                    
            except Exception as e:
                self.logger.error(f"Failed to update statistics for tenant {tenant_name}: {e}")
    
    async def list_script_elements(self) -> Dict[str, Any]:
        """List all script-inserted elements without removing them."""
        self.logger.info("🔍 Listing all script-inserted elements...")
        
        elements = await Element.find({
            "insertion_batch_id": {"$exists": True, "$ne": None}
        }).to_list()
        
        if not elements:
            return {"message": "No script-inserted elements found", "elements": []}
        
        # Group by various criteria
        batch_groups = {}
        tenant_groups = {}
        project_groups = {}
        
        for element in elements:
            # By batch
            batch_id = element.insertion_batch_id
            if batch_id not in batch_groups:
                batch_groups[batch_id] = []
            batch_groups[batch_id].append(element)
            
            # By tenant
            tenant = element.tenant_type.value
            if tenant not in tenant_groups:
                tenant_groups[tenant] = []
            tenant_groups[tenant].append(element)
            
            # By project
            project_id = element.project_id
            if project_id not in project_groups:
                project_groups[project_id] = []
            project_groups[project_id].append(element)
        
        return {
            "total_elements": len(elements),
            "batch_count": len(batch_groups),
            "tenant_count": len(tenant_groups),
            "project_count": len(project_groups),
            "batch_distribution": {
                batch_id: len(batch_elements)
                for batch_id, batch_elements in batch_groups.items()
            },
            "tenant_distribution": {
                tenant: len(tenant_elements)
                for tenant, tenant_elements in tenant_groups.items()
            },
            "project_distribution": {
                project_id: len(project_elements)
                for project_id, project_elements in project_groups.items()
            },
            "elements": [
                {
                    "id": str(element.id),
                    "name": element.name,
                    "tenant": element.tenant_type.value,
                    "element_type": element.element_type.value,
                    "batch_id": element.insertion_batch_id,
                    "project_id": element.project_id,
                    "template_id": element.template_id,
                    "is_default": element.is_default_element,
                    "created_at": element.created_at.isoformat() if element.created_at else None
                }
                for element in elements
            ]
        }


async def main():
    """Main function to run the script element remover."""
    parser = argparse.ArgumentParser(
        description="Remove elements inserted by scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all script-inserted elements
  python remove_script_elements.py --list

  # Dry run - show what would be removed
  python remove_script_elements.py --dry-run

  # Remove all script-inserted elements
  python remove_script_elements.py --force

  # Remove elements for specific tenant
  python remove_script_elements.py --tenant hr --force

  # Remove elements from specific batch
  python remove_script_elements.py --batch-id batch_20241201_143022 --force

  # Remove default elements from project
  python remove_script_elements.py --project-id 507f1f77bcf86cd799439012 --default-only --force
        """
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all script-inserted elements without removing them"
    )
    
    parser.add_argument(
        "--tenant",
        type=str,
        choices=[t.value for t in TenantType],
        help="Remove elements for specific tenant type"
    )
    
    parser.add_argument(
        "--batch-id",
        type=str,
        help="Remove elements from specific batch ID"
    )
    
    parser.add_argument(
        "--project-id",
        type=str,
        help="Remove elements from specific project"
    )
    
    parser.add_argument(
        "--default-only",
        action="store_true",
        help="Only remove default elements (use with --project-id)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts"
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
            document_models=[Element, ElementTemplate, TenantConfiguration]
        )
        logger.info("✅ Database connected successfully")
        
        # Initialize remover
        remover = ScriptElementRemover()
        
        # Execute based on arguments
        if args.list:
            report = await remover.list_script_elements()
            print("\n📊 SCRIPT ELEMENTS REPORT:")
            print(f"Total Elements: {report['total_elements']}")
            print(f"Batches: {report['batch_count']}")
            print(f"Tenants: {report['tenant_count']}")
            print(f"Projects: {report['project_count']}")
            
            if report['total_elements'] > 0:
                print("\nBatch Distribution:")
                for batch_id, count in report['batch_distribution'].items():
                    print(f"  • {batch_id}: {count} elements")
                
                print("\nTenant Distribution:")
                for tenant, count in report['tenant_distribution'].items():
                    print(f"  • {tenant}: {count} elements")
        
        elif args.tenant:
            tenant_type = TenantType(args.tenant)
            report = await remover.remove_by_tenant(
                tenant_type=tenant_type,
                dry_run=args.dry_run,
                force=args.force
            )
            print(f"\n✅ Tenant removal complete: {report}")
        
        elif args.batch_id:
            report = await remover.remove_by_batch(
                batch_id=args.batch_id,
                dry_run=args.dry_run,
                force=args.force
            )
            print(f"\n✅ Batch removal complete: {report}")
        
        elif args.project_id:
            report = await remover.remove_by_project(
                project_id=args.project_id,
                default_only=args.default_only,
                dry_run=args.dry_run,
                force=args.force
            )
            print(f"\n✅ Project removal complete: {report}")
        
        else:
            # Remove all script elements
            report = await remover.remove_all_script_elements(
                dry_run=args.dry_run,
                force=args.force
            )
            print(f"\n✅ Removal complete: {report}")
        
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