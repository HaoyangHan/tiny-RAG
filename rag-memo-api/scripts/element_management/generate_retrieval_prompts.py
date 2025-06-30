#!/usr/bin/env python3
"""
Generate Retrieval Prompts - TinyRAG v1.4

This script generates retrieval prompts for elements that have generation prompts
but are missing retrieval prompts, using the LLM summarization service.
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Element, ElementTemplate
from models.enums import TenantType
from services.prompt_summarization_service import get_summarization_service
from database import get_database_url


class RetrievalPromptGenerator:
    """
    Service for generating retrieval prompts from generation prompts.
    
    Uses the LLM summarization service to automatically generate
    concise, searchable retrieval prompts from detailed generation prompts.
    """
    
    def __init__(self):
        """Initialize the retrieval prompt generator."""
        self.logger = logging.getLogger(__name__)
        self.summarization_service = get_summarization_service()
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.processing_report: Dict[str, Any] = {}
    
    async def generate_for_all_missing(
        self,
        tenant_type: Optional[TenantType] = None,
        project_id: Optional[str] = None,
        limit: Optional[int] = None,
        batch_size: int = 5,
        show_progress: bool = False
    ) -> Dict[str, Any]:
        """
        Generate retrieval prompts for all elements missing them.
        
        Args:
            tenant_type: Filter by tenant type
            project_id: Filter by project ID
            limit: Maximum number of elements to process
            batch_size: Number of elements to process in parallel
            show_progress: Whether to show progress updates
            
        Returns:
            Processing report with statistics
        """
        self.logger.info("🔍 Finding elements without retrieval prompts...")
        
        # Build query for elements with generation prompts but missing retrieval prompts
        query = {
            "$or": [
                {"template.generation_prompt": {"$exists": True, "$ne": None, "$ne": ""}},
                {"template.content": {"$exists": True, "$ne": None, "$ne": ""}}
            ],
            "$and": [
                {
                    "$or": [
                        {"template.retrieval_prompt": {"$exists": False}},
                        {"template.retrieval_prompt": None},
                        {"template.retrieval_prompt": ""}
                    ]
                }
            ]
        }
        
        if tenant_type:
            query["tenant_type"] = tenant_type
        if project_id:
            query["project_id"] = project_id
        
        elements = await Element.find(query).limit(limit or 1000).to_list()
        
        if not elements:
            self.logger.info("✅ No elements found that need retrieval prompts")
            return {
                "message": "No elements need retrieval prompts",
                "processed": 0,
                "successful": 0,
                "failed": 0
            }
        
        self.logger.info(f"📊 Found {len(elements)} elements without retrieval prompts")
        
        # Show distribution
        tenant_distribution = {}
        element_type_distribution = {}
        
        for element in elements:
            tenant = element.tenant_type.value
            element_type = element.element_type.value
            
            tenant_distribution[tenant] = tenant_distribution.get(tenant, 0) + 1
            element_type_distribution[element_type] = element_type_distribution.get(element_type, 0) + 1
        
        self.logger.info("📈 Distribution:")
        for tenant, count in tenant_distribution.items():
            self.logger.info(f"   • {tenant}: {count} elements")
        for elem_type, count in element_type_distribution.items():
            self.logger.info(f"   • {elem_type}: {count} elements")
        
        # Process elements
        return await self._process_elements(
            elements=elements,
            batch_size=batch_size,
            show_progress=show_progress
        )
    
    async def generate_for_specific_elements(
        self,
        element_ids: List[str],
        batch_size: int = 5,
        show_progress: bool = False
    ) -> Dict[str, Any]:
        """
        Generate retrieval prompts for specific elements.
        
        Args:
            element_ids: List of element IDs to process
            batch_size: Number of elements to process in parallel
            show_progress: Whether to show progress updates
            
        Returns:
            Processing report
        """
        self.logger.info(f"🔍 Processing {len(element_ids)} specific elements...")
        
        # Find elements
        from bson import ObjectId
        elements = await Element.find({
            "_id": {"$in": [ObjectId(eid) for eid in element_ids]}
        }).to_list()
        
        if not elements:
            self.logger.warning("⚠️  No elements found with provided IDs")
            return {
                "message": "No elements found",
                "processed": 0,
                "successful": 0,
                "failed": 0
            }
        
        found_ids = [str(elem.id) for elem in elements]
        missing_ids = [eid for eid in element_ids if eid not in found_ids]
        
        if missing_ids:
            self.logger.warning(f"⚠️  {len(missing_ids)} element IDs not found: {missing_ids}")
        
        return await self._process_elements(
            elements=elements,
            batch_size=batch_size,
            show_progress=show_progress
        )
    
    async def regenerate_all_retrieval_prompts(
        self,
        tenant_type: Optional[TenantType] = None,
        element_ids: Optional[List[str]] = None,
        force: bool = False,
        batch_size: int = 5,
        show_progress: bool = False
    ) -> Dict[str, Any]:
        """
        Regenerate retrieval prompts for elements (including those that already have them).
        
        Args:
            tenant_type: Filter by tenant type
            element_ids: Specific element IDs to process
            force: Whether to overwrite existing retrieval prompts
            batch_size: Number of elements to process in parallel
            show_progress: Whether to show progress updates
            
        Returns:
            Processing report
        """
        self.logger.info("🔄 Regenerating retrieval prompts...")
        
        # Build query
        query = {
            "$or": [
                {"template.generation_prompt": {"$exists": True, "$ne": None, "$ne": ""}},
                {"template.content": {"$exists": True, "$ne": None, "$ne": ""}}
            ]
        }
        
        if not force:
            # Only process elements without retrieval prompts
            query["$and"] = [
                {
                    "$or": [
                        {"template.retrieval_prompt": {"$exists": False}},
                        {"template.retrieval_prompt": None},
                        {"template.retrieval_prompt": ""}
                    ]
                }
            ]
        
        if tenant_type:
            query["tenant_type"] = tenant_type
        
        if element_ids:
            from bson import ObjectId
            query["_id"] = {"$in": [ObjectId(eid) for eid in element_ids]}
        
        elements = await Element.find(query).to_list()
        
        if not elements:
            self.logger.info("✅ No elements found to regenerate")
            return {
                "message": "No elements to regenerate",
                "processed": 0,
                "successful": 0,
                "failed": 0
            }
        
        action = "regenerating" if force else "generating missing"
        self.logger.info(f"📊 Found {len(elements)} elements for {action} retrieval prompts")
        
        return await self._process_elements(
            elements=elements,
            batch_size=batch_size,
            show_progress=show_progress,
            force_regenerate=force
        )
    
    async def _process_elements(
        self,
        elements: List[Element],
        batch_size: int = 5,
        show_progress: bool = False,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """Process elements to generate retrieval prompts."""
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        
        failed_elements = []
        successful_elements = []
        
        # Process in batches
        for i in range(0, len(elements), batch_size):
            batch = elements[i:i + batch_size]
            
            if show_progress:
                progress = (i / len(elements)) * 100
                self.logger.info(f"🔄 Processing batch {i//batch_size + 1} ({progress:.1f}% complete)")
            
            # Prepare prompts and contexts for batch processing
            batch_prompts = []
            batch_contexts = []
            valid_elements = []
            
            for element in batch:
                # Get generation prompt
                generation_prompt = self._get_generation_prompt(element)
                
                if not generation_prompt:
                    self.logger.warning(f"⚠️  Element {element.name} has no generation prompt, skipping")
                    continue
                
                # Check if already has retrieval prompt (unless force regenerating)
                if not force_regenerate and element.has_retrieval_prompt():
                    self.logger.debug(f"✅ Element {element.name} already has retrieval prompt, skipping")
                    continue
                
                batch_prompts.append(generation_prompt)
                batch_contexts.append({
                    'tenant_type': element.tenant_type,
                    'element_type': element.element_type,
                    'element_name': element.name
                })
                valid_elements.append(element)
            
            if not batch_prompts:
                continue
            
            try:
                # Generate retrieval prompts for batch
                retrieval_prompts = await self.summarization_service.batch_summarize_prompts(
                    prompts=batch_prompts,
                    contexts=batch_contexts
                )
                
                # Update elements
                for element, retrieval_prompt in zip(valid_elements, retrieval_prompts):
                    try:
                        element.update_retrieval_prompt(retrieval_prompt)
                        await element.save()
                        
                        successful_elements.append({
                            "id": str(element.id),
                            "name": element.name,
                            "tenant": element.tenant_type.value,
                            "retrieval_prompt_length": len(retrieval_prompt)
                        })
                        self.success_count += 1
                        
                        self.logger.debug(f"✅ Generated retrieval prompt for: {element.name}")
                        
                    except Exception as e:
                        failed_elements.append({
                            "id": str(element.id),
                            "name": element.name,
                            "error": str(e)
                        })
                        self.error_count += 1
                        self.logger.error(f"❌ Failed to update element {element.name}: {e}")
                
                self.processed_count += len(valid_elements)
                
            except Exception as e:
                self.logger.error(f"❌ Batch processing failed: {e}")
                for element in valid_elements:
                    failed_elements.append({
                        "id": str(element.id),
                        "name": element.name,
                        "error": f"Batch processing failed: {str(e)}"
                    })
                self.error_count += len(valid_elements)
        
        # Generate final report
        report = {
            "operation": "generate_retrieval_prompts",
            "total_elements": len(elements),
            "processed": self.processed_count,
            "successful": self.success_count,
            "failed": self.error_count,
            "success_rate": round((self.success_count / max(1, self.processed_count)) * 100, 2),
            "successful_elements": successful_elements,
            "failed_elements": failed_elements,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Processing complete:")
        self.logger.info(f"   • Processed: {self.processed_count} elements")
        self.logger.info(f"   • Successful: {self.success_count} elements")
        self.logger.info(f"   • Failed: {self.error_count} elements")
        self.logger.info(f"   • Success rate: {report['success_rate']:.1f}%")
        
        return report
    
    def _get_generation_prompt(self, element: Element) -> Optional[str]:
        """Get the generation prompt from an element."""
        # Try new generation_prompt field first
        if element.template.generation_prompt:
            return element.template.generation_prompt
        
        # Fall back to legacy content field
        if element.template.content:
            return element.template.content
        
        return None
    
    async def validate_prompt_quality(
        self,
        element_id: str,
        show_details: bool = False
    ) -> Dict[str, Any]:
        """
        Validate the quality of retrieval prompt for an element.
        
        Args:
            element_id: Element ID to validate
            show_details: Whether to include detailed metrics
            
        Returns:
            Validation report
        """
        # Find element
        element = await Element.get(element_id)
        if not element:
            raise ValueError(f"Element not found: {element_id}")
        
        generation_prompt = self._get_generation_prompt(element)
        retrieval_prompt = element.template.retrieval_prompt
        
        if not generation_prompt:
            return {"error": "Element has no generation prompt"}
        
        if not retrieval_prompt:
            return {"error": "Element has no retrieval prompt"}
        
        # Use summarization service to validate quality
        context = {
            'tenant_type': element.tenant_type,
            'element_type': element.element_type,
            'element_name': element.name
        }
        
        metrics = await self.summarization_service.validate_prompt_quality(
            generation_prompt=generation_prompt,
            retrieval_prompt=retrieval_prompt,
            context=context
        )
        
        validation_report = {
            "element_id": element_id,
            "element_name": element.name,
            "tenant_type": element.tenant_type.value,
            "validation_score": min(1.0, (metrics["completeness_score"] + metrics["readability_score"]) / 2),
            "quality_rating": "Good" if metrics["completeness_score"] > 0.7 else "Fair" if metrics["completeness_score"] > 0.4 else "Poor",
            "compression_ratio": metrics["compression_ratio"],
            "length_ratio": metrics["length_ratio"]
        }
        
        if show_details:
            validation_report["detailed_metrics"] = metrics
            validation_report["generation_prompt"] = generation_prompt
            validation_report["retrieval_prompt"] = retrieval_prompt
        
        return validation_report


async def main():
    """Main function to run the retrieval prompt generator."""
    parser = argparse.ArgumentParser(
        description="Generate retrieval prompts for elements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate retrieval prompts for all elements missing them
  python generate_retrieval_prompts.py

  # Generate for specific tenant
  python generate_retrieval_prompts.py --tenant hr

  # Generate for specific elements
  python generate_retrieval_prompts.py --element-ids 507f1f77bcf86cd799439011,507f1f77bcf86cd799439012

  # Regenerate all (overwrite existing)
  python generate_retrieval_prompts.py --regenerate-all

  # Custom settings with progress tracking
  python generate_retrieval_prompts.py --batch-size 10 --show-progress

  # Validate prompt quality
  python generate_retrieval_prompts.py --validate 507f1f77bcf86cd799439011
        """
    )
    
    parser.add_argument(
        "--tenant",
        type=str,
        choices=[t.value for t in TenantType],
        help="Filter by tenant type"
    )
    
    parser.add_argument(
        "--project-id",
        type=str,
        help="Filter by project ID"
    )
    
    parser.add_argument(
        "--element-ids",
        type=str,
        help="Comma-separated list of element IDs to process"
    )
    
    parser.add_argument(
        "--regenerate-all",
        action="store_true",
        help="Regenerate all retrieval prompts (overwrite existing)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Batch size for parallel processing (default: 5)"
    )
    
    parser.add_argument(
        "--show-progress",
        action="store_true",
        help="Show progress updates during processing"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of elements to process"
    )
    
    parser.add_argument(
        "--validate",
        type=str,
        help="Validate prompt quality for specific element ID"
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
            document_models=[Element, ElementTemplate]
        )
        logger.info("✅ Database connected successfully")
        
        # Initialize generator
        generator = RetrievalPromptGenerator()
        
        # Execute based on arguments
        if args.validate:
            report = await generator.validate_prompt_quality(
                element_id=args.validate,
                show_details=True
            )
            print("\n📊 PROMPT QUALITY VALIDATION:")
            print(f"Element: {report.get('element_name', 'Unknown')}")
            print(f"Quality Rating: {report.get('quality_rating', 'Unknown')}")
            print(f"Validation Score: {report.get('validation_score', 0):.2f}")
            print(f"Compression Ratio: {report.get('compression_ratio', 0):.2f}")
            
            if 'detailed_metrics' in report:
                print(f"\nDetailed Metrics:")
                for key, value in report['detailed_metrics'].items():
                    print(f"  • {key}: {value}")
        
        elif args.element_ids:
            element_ids = [eid.strip() for eid in args.element_ids.split(',')]
            report = await generator.generate_for_specific_elements(
                element_ids=element_ids,
                batch_size=args.batch_size,
                show_progress=args.show_progress
            )
            print(f"\n✅ Specific elements processing complete: {report}")
        
        elif args.regenerate_all:
            tenant_type = TenantType(args.tenant) if args.tenant else None
            report = await generator.regenerate_all_retrieval_prompts(
                tenant_type=tenant_type,
                force=True,
                batch_size=args.batch_size,
                show_progress=args.show_progress
            )
            print(f"\n✅ Regeneration complete: {report}")
        
        else:
            # Generate for missing retrieval prompts
            tenant_type = TenantType(args.tenant) if args.tenant else None
            report = await generator.generate_for_all_missing(
                tenant_type=tenant_type,
                project_id=args.project_id,
                limit=args.limit,
                batch_size=args.batch_size,
                show_progress=args.show_progress
            )
            print(f"\n✅ Generation complete: {report}")
        
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