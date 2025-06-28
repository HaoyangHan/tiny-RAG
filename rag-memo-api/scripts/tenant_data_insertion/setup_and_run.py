"""
Setup and run script for tenant element insertion.

This script helps set up the environment and run tenant element insertions
with proper error handling and validation.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# Add the rag-memo-api to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.enums import TenantType
from config import MONGODB_URL, DATABASE_NAME, DEFAULT_PROJECT_IDS, DRY_RUN


class SetupManager:
    """Manager for setting up and validating the tenant insertion environment."""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.api_dir = self.script_dir.parent
    
    def validate_environment(self) -> bool:
        """
        Validate that the environment is properly configured.
        
        Returns:
            bool: True if environment is valid, False otherwise
        """
        print("🔍 Validating environment...")
        
        # Check MongoDB URL
        if not MONGODB_URL:
            print("❌ MONGODB_URL not configured")
            return False
        print(f"✅ MongoDB URL: {MONGODB_URL}")
        
        # Check database name
        if not DATABASE_NAME:
            print("❌ DATABASE_NAME not configured")
            return False
        print(f"✅ Database name: {DATABASE_NAME}")
        
        # Check project IDs
        missing_projects = []
        for tenant_type, project_id in DEFAULT_PROJECT_IDS.items():
            if not project_id or project_id.startswith("60f4d2e5e8b4a123456789"):
                missing_projects.append(tenant_type.value)
        
        if missing_projects:
            print(f"⚠️ Default project IDs need updating for: {', '.join(missing_projects)}")
            print("   Please update config.py with actual project IDs from your database")
        
        # Check if models can be imported
        try:
            from models.element import Element
            from models.project import Project
            print("✅ Models imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import models: {e}")
            return False
        
        print("✅ Environment validation complete")
        return True
    
    def print_usage_instructions(self):
        """Print detailed usage instructions."""
        print("\n" + "="*70)
        print("📚 TENANT ELEMENT INSERTION USAGE GUIDE")
        print("="*70)
        
        print("\n🚀 **Quick Start:**")
        print("1. Ensure TinyRAG services are running:")
        print("   cd ../.. && docker-compose up -d")
        print("\n2. Update configuration:")
        print("   Edit config.py with your actual project IDs")
        print("\n3. Run insertions:")
        print("   python insert_all.py")
        
        print("\n⚙️ **Configuration Options:**")
        print("   DRY_RUN = True   # Test mode (no actual insertions)")
        print("   DRY_RUN = False  # Production mode (actual insertions)")
        
        print("\n📋 **Available Commands:**")
        print("   # Run all tenants sequentially")
        print("   python insert_all.py")
        print("\n   # Run all tenants in parallel")
        print("   python insert_all.py --parallel")
        print("\n   # Run specific tenants only")
        print("   python insert_all.py --tenants hr coding")
        print("\n   # Run individual tenant")
        print("   python tenant_hr_elements.py")
        
        print("\n🏢 **Available Tenant Types:**")
        implemented = ["hr", "coding", "financial_report"]
        todo = ["deep_research", "qa_generation", "raw_rag"]
        
        for tenant in implemented:
            print(f"   ✅ {tenant} - Fully implemented")
        for tenant in todo:
            print(f"   🚧 {tenant} - Placeholder (needs implementation)")
        
        print("\n🔧 **Customization:**")
        print("   - Edit tenant_*_elements.py files to modify element definitions")
        print("   - Update config.py for project IDs and settings")
        print("   - Implement placeholder tenants as needed")
        
        print("\n⚠️ **Important Notes:**")
        print("   - Always test with DRY_RUN=True first")
        print("   - Ensure project IDs exist in your database")
        print("   - Check logs for detailed error information")
        print("   - Duplicate elements will be skipped automatically")
        
        print("="*70)
    
    async def test_database_connection(self) -> bool:
        """
        Test the database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        print("\n🔗 Testing database connection...")
        
        try:
            import motor.motor_asyncio
            from beanie import init_beanie
            from models.element import Element
            from models.project import Project
            
            # Test connection
            client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
            database = client[DATABASE_NAME]
            
            # Test with a simple operation
            await init_beanie(
                database=database,
                document_models=[Element, Project]
            )
            
            # Try to count documents (this will work even if collections don't exist)
            project_count = await Project.count()
            element_count = await Element.count()
            
            print(f"✅ Database connection successful")
            print(f"   Projects in database: {project_count}")
            print(f"   Elements in database: {element_count}")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("   Please check your MongoDB service and connection string")
            return False
    
    async def run_dry_run_test(self) -> bool:
        """
        Run a quick dry run test to validate everything works.
        
        Returns:
            bool: True if test successful, False otherwise
        """
        print("\n🧪 Running dry run test...")
        
        try:
            # Import and run a single tenant in dry run mode
            from tenant_hr_elements import HRElementInserter
            
            # Temporarily set dry run mode
            original_dry_run = DRY_RUN
            import config
            config.DRY_RUN = True
            
            inserter = HRElementInserter(TenantType.HR)
            result = await inserter.run()
            
            # Restore original setting
            config.DRY_RUN = original_dry_run
            
            if result.get("error"):
                print(f"❌ Dry run test failed: {result['error']}")
                return False
            
            print(f"✅ Dry run test successful")
            print(f"   Would insert {result.get('total_elements', 0)} HR elements")
            
            return True
            
        except Exception as e:
            print(f"❌ Dry run test failed: {e}")
            return False


async def main():
    """Main setup and validation function."""
    print("🎯 TinyRAG Tenant Element Insertion Setup")
    print("="*50)
    
    setup = SetupManager()
    
    # Validate environment
    if not setup.validate_environment():
        print("\n❌ Environment validation failed. Please fix the issues above.")
        return False
    
    # Test database connection
    if not await setup.test_database_connection():
        print("\n❌ Database connection test failed. Please fix the connection issues.")
        return False
    
    # Run dry run test
    if not await setup.run_dry_run_test():
        print("\n❌ Dry run test failed. Please check the configuration.")
        return False
    
    print("\n🎉 Setup validation complete! Your environment is ready.")
    
    # Show usage instructions
    setup.print_usage_instructions()
    
    # Offer to run insertions
    if not DRY_RUN:
        print("\n❓ Ready to run element insertions now? (y/N): ", end="")
        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                print("\n🚀 Running element insertions...")
                from insert_all import MasterElementInserter
                
                inserter = MasterElementInserter()
                summary = await inserter.run_all_parallel()
                inserter.print_summary(summary)
                
                return summary["master_summary"]["tenants_with_errors"] == 0
        except KeyboardInterrupt:
            print("\n⏹️ Cancelled by user")
    else:
        print(f"\n💡 Currently in DRY_RUN mode. Set DRY_RUN=False in config.py to perform actual insertions.")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 