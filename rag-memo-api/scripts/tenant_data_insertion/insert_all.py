"""
Master script for running all tenant-specific element insertions.

This script orchestrates the insertion of predefined elements across all
tenant types in the TinyRAG system.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from models.enums import TenantType
from .config import LOGGING_CONFIG, DRY_RUN

# Import all tenant inserters
from .tenant_hr_elements import HRElementInserter
from .tenant_coding_elements import CodingElementInserter  
from .tenant_financial_elements import FinancialElementTemplateInserter

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Define tenant inserter mapping
TENANT_INSERTERS = {
    TenantType.HR: HRElementInserter,
    TenantType.CODING: CodingElementInserter,
    TenantType.FINANCIAL_REPORT: FinancialElementTemplateInserter,
    # Add more tenant inserters as they are created:
    # TenantType.DEEP_RESEARCH: ResearchElementInserter,
    # TenantType.QA_GENERATION: QAElementInserter,
    # TenantType.RAW_RAG: RawRAGElementInserter,
}


class MasterElementInserter:
    """Master inserter for orchestrating all tenant element insertions."""
    
    def __init__(self, tenant_types: List[TenantType] = None):
        """
        Initialize the master inserter.
        
        Args:
            tenant_types: List of tenant types to process. If None, processes all available.
        """
        self.tenant_types = tenant_types or list(TENANT_INSERTERS.keys())
        self.results: Dict[TenantType, Dict[str, Any]] = {}
        self.start_time = None
        self.end_time = None
    
    async def run_tenant_insertion(self, tenant_type: TenantType) -> Dict[str, Any]:
        """
        Run element insertion for a specific tenant type.
        
        Args:
            tenant_type: The tenant type to process
            
        Returns:
            Dict[str, Any]: Insertion results for the tenant
        """
        if tenant_type not in TENANT_INSERTERS:
            logger.error(f"No inserter found for tenant type: {tenant_type}")
            return {
                "error": f"No inserter available for tenant type: {tenant_type}",
                "tenant_type": tenant_type.value
            }
        
        logger.info(f"🚀 Starting element insertion for tenant: {tenant_type.value}")
        
        try:
            inserter_class = TENANT_INSERTERS[tenant_type]
            inserter = inserter_class(tenant_type)
            result = await inserter.run()
            
            # Add tenant-specific timing and metadata
            result["execution_time"] = datetime.utcnow().isoformat()
            result["inserter_class"] = inserter_class.__name__
            
            if result.get("error"):
                logger.error(f"❌ Failed to insert elements for {tenant_type.value}: {result['error']}")
            else:
                success_count = result.get("successful", 0)
                logger.info(f"✅ Successfully inserted {success_count} elements for {tenant_type.value}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Unexpected error processing {tenant_type.value}: {str(e)}")
            return {
                "error": str(e),
                "tenant_type": tenant_type.value,
                "execution_time": datetime.utcnow().isoformat()
            }
    
    async def run_all_sequential(self) -> Dict[str, Any]:
        """
        Run all tenant insertions sequentially.
        
        Returns:
            Dict[str, Any]: Combined results from all tenant insertions
        """
        logger.info(f"📋 Starting sequential insertion for {len(self.tenant_types)} tenants")
        self.start_time = datetime.utcnow()
        
        for tenant_type in self.tenant_types:
            result = await self.run_tenant_insertion(tenant_type)
            self.results[tenant_type] = result
        
        self.end_time = datetime.utcnow()
        return self._generate_summary()
    
    async def run_all_parallel(self) -> Dict[str, Any]:
        """
        Run all tenant insertions in parallel.
        
        Returns:
            Dict[str, Any]: Combined results from all tenant insertions
        """
        logger.info(f"⚡ Starting parallel insertion for {len(self.tenant_types)} tenants")
        self.start_time = datetime.utcnow()
        
        # Create tasks for all tenant insertions
        tasks = [
            self.run_tenant_insertion(tenant_type) 
            for tenant_type in self.tenant_types
        ]
        
        # Run all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            tenant_type = self.tenant_types[i]
            if isinstance(result, Exception):
                logger.error(f"❌ Exception for {tenant_type.value}: {str(result)}")
                self.results[tenant_type] = {
                    "error": str(result),
                    "tenant_type": tenant_type.value,
                    "execution_time": datetime.utcnow().isoformat()
                }
            else:
                self.results[tenant_type] = result
        
        self.end_time = datetime.utcnow()
        return self._generate_summary()
    
    def _generate_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of all insertions.
        
        Returns:
            Dict[str, Any]: Summary of all tenant insertions
        """
        total_elements = 0
        total_successful = 0
        total_failed = 0
        total_skipped = 0
        tenants_with_errors = []
        all_inserted_ids = []
        
        for tenant_type, result in self.results.items():
            if result.get("error"):
                tenants_with_errors.append(tenant_type.value)
            else:
                total_elements += result.get("total_elements", 0)
                total_successful += result.get("successful", 0)
                total_failed += result.get("failed", 0)
                total_skipped += result.get("skipped", 0)
                all_inserted_ids.extend(result.get("inserted_ids", []))
        
        execution_duration = None
        if self.start_time and self.end_time:
            execution_duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "master_summary": {
                "execution_start": self.start_time.isoformat() if self.start_time else None,
                "execution_end": self.end_time.isoformat() if self.end_time else None,
                "execution_duration_seconds": execution_duration,
                "tenants_processed": len(self.tenant_types),
                "tenants_with_errors": len(tenants_with_errors),
                "total_elements": total_elements,
                "total_successful": total_successful,
                "total_failed": total_failed,
                "total_skipped": total_skipped,
                "total_inserted_elements": len(all_inserted_ids),
                "dry_run": DRY_RUN
            },
            "tenant_results": {tenant.value: result for tenant, result in self.results.items()},
            "error_tenants": tenants_with_errors,
            "all_inserted_ids": all_inserted_ids
        }
    
    def print_summary(self, summary: Dict[str, Any]) -> None:
        """
        Print a formatted summary of the insertion results.
        
        Args:
            summary: The summary dictionary to print
        """
        master = summary["master_summary"]
        
        print("\n" + "="*80)
        print("🎯 MASTER ELEMENT INSERTION SUMMARY")
        print("="*80)
        
        print(f"📊 **Execution Overview:**")
        print(f"   ⏰ Start Time: {master['execution_start']}")
        print(f"   ⏰ End Time: {master['execution_end']}")
        print(f"   ⏱️  Duration: {master['execution_duration_seconds']:.2f} seconds")
        print(f"   🏢 Tenants Processed: {master['tenants_processed']}")
        print(f"   🔄 Dry Run Mode: {'Yes' if master['dry_run'] else 'No'}")
        
        print(f"\n📈 **Overall Results:**")
        print(f"   📝 Total Elements: {master['total_elements']}")
        print(f"   ✅ Successful: {master['total_successful']}")
        print(f"   ❌ Failed: {master['total_failed']}")
        print(f"   ⏭️  Skipped: {master['total_skipped']}")
        print(f"   🆔 Total Inserted IDs: {master['total_inserted_elements']}")
        
        if master["tenants_with_errors"]:
            print(f"\n⚠️  **Tenants with Errors:** {', '.join(summary['error_tenants'])}")
        
        print(f"\n📋 **Per-Tenant Results:**")
        for tenant_name, result in summary["tenant_results"].items():
            if result.get("error"):
                print(f"   ❌ {tenant_name}: ERROR - {result['error']}")
            else:
                print(f"   ✅ {tenant_name}: {result.get('successful', 0)}/{result.get('total_elements', 0)} successful")
        
        if master["total_inserted_elements"] > 0 and not master["dry_run"]:
            print(f"\n🆔 **Sample Inserted Element IDs:**")
            sample_ids = summary["all_inserted_ids"][:5]  # Show first 5 IDs
            for eid in sample_ids:
                print(f"   - {eid}")
            if len(summary["all_inserted_ids"]) > 5:
                print(f"   ... and {len(summary['all_inserted_ids']) - 5} more")
        
        print("="*80)


async def main():
    """Main function to run all tenant element insertions."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Insert predefined elements for all tenants")
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="Run insertions in parallel (default: sequential)"
    )
    parser.add_argument(
        "--tenants",
        nargs="+",
        choices=[t.value for t in TenantType],
        help="Specific tenant types to process (default: all available)"
    )
    
    args = parser.parse_args()
    
    # Filter tenant types if specified
    tenant_types = None
    if args.tenants:
        tenant_types = [TenantType(t) for t in args.tenants]
    
    # Create and run master inserter
    inserter = MasterElementInserter(tenant_types)
    
    if args.parallel:
        logger.info("🚀 Running in parallel mode")
        summary = await inserter.run_all_parallel()
    else:
        logger.info("🚀 Running in sequential mode")
        summary = await inserter.run_all_sequential()
    
    # Print summary
    inserter.print_summary(summary)
    
    # Exit with error code if there were failures
    if summary["master_summary"]["tenants_with_errors"] > 0:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 