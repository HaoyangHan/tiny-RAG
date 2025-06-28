"""
Script to create placeholder element insertion files for remaining tenant types.

This script generates skeleton files for the remaining tenant types that
haven't been implemented yet.
"""

import os
from pathlib import Path
from models.enums import TenantType, TENANT_TASK_MAPPING

# Map of tenant types to their implementation status
IMPLEMENTED_TENANTS = {
    TenantType.HR,
    TenantType.CODING, 
    TenantType.FINANCIAL_REPORT
}

REMAINING_TENANTS = {
    TenantType.DEEP_RESEARCH,
    TenantType.QA_GENERATION,
    TenantType.RAW_RAG
}

def create_tenant_file(tenant_type: TenantType, script_dir: Path) -> None:
    """
    Create a skeleton tenant insertion script.
    
    Args:
        tenant_type: The tenant type to create a script for
        script_dir: Directory to create the script in
    """
    tenant_name = tenant_type.value
    class_name = f"{''.join(word.capitalize() for word in tenant_name.split('_'))}ElementInserter"
    file_name = f"tenant_{tenant_name}_elements.py"
    task_type = TENANT_TASK_MAPPING.get(tenant_type, "RAG")
    
    template = f'''"""
{tenant_name.replace('_', ' ').title()} Tenant Element Insertion Script.

This script contains predefined elements for {tenant_name.replace('_', ' ').title()} tenant type.
TODO: Implement specific elements for this tenant type.
"""

import asyncio
from typing import List, Dict, Any

from models.enums import TenantType, TaskType, ElementType, ElementStatus
from .base_inserter import BaseElementInserter


class {class_name}(BaseElementInserter):
    """Element inserter for {tenant_name.replace('_', ' ').title()} tenant type."""
    
    def get_elements_data(self) -> List[Dict[str, Any]]:
        """
        Get predefined {tenant_name.replace('_', ' ').title()} elements.
        
        TODO: Implement specific elements for this tenant type.
        
        Returns:
            List[Dict[str, Any]]: List of {tenant_name.replace('_', ' ').title()} element data
        """
        # TODO: Replace this placeholder with actual element definitions
        return [
            {{
                "name": "Sample {tenant_name.replace('_', ' ').title()} Template",
                "description": "TODO: Implement specific template for {tenant_name.replace('_', ' ').lower()}",
                "task_type": TaskType.{task_type},
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.DRAFT,
                "template": self.create_element_template(
                    content="TODO: Implement template content for {tenant_name.replace('_', ' ').lower()}\\n\\n" +
                           "Template variables: {{variable_name}}\\n\\n" +
                           "This is a placeholder template that needs to be implemented.",
                    variables=["variable_name"],
                    execution_config={{
                        "temperature": 0.5,
                        "max_tokens": 2000,
                        "model": "gpt-4o-mini"
                    }}
                ),
                "tags": self.create_element_tags(["placeholder", "todo", "sample"])
            }}
        ]


async def main():
    """Main function to run {tenant_name.replace('_', ' ').title()} element insertion."""
    inserter = {class_name}(TenantType.{tenant_type.name})
    result = await inserter.run()
    
    print("\\n" + "="*50)
    print("{tenant_name.replace('_', ' ').upper()} ELEMENT INSERTION SUMMARY")
    print("="*50)
    print(f"Tenant Type: {{result.get('tenant_type', 'Unknown')}}")
    print(f"Total Elements: {{result.get('total_elements', 0)}}")
    print(f"Successful: {{result.get('successful', 0)}}")
    print(f"Failed: {{result.get('failed', 0)}}")
    print(f"Skipped: {{result.get('skipped', 0)}}")
    print(f"Dry Run: {{result.get('dry_run', False)}}")
    
    if result.get('inserted_ids'):
        print(f"\\nInserted Element IDs:")
        for element_id in result['inserted_ids']:
            print(f"  - {{element_id}}")
    
    if result.get('error'):
        print(f"\\nError: {{result['error']}}")
    
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
'''

    file_path = script_dir / file_name
    
    with open(file_path, 'w') as f:
        f.write(template)
    
    print(f"✅ Created {file_name}")


def main():
    """Create placeholder files for remaining tenant types."""
    script_dir = Path(__file__).parent
    
    print("Creating placeholder files for remaining tenant types...")
    print(f"Target directory: {script_dir}")
    
    for tenant_type in REMAINING_TENANTS:
        create_tenant_file(tenant_type, script_dir)
    
    print(f"\\n🎉 Created {len(REMAINING_TENANTS)} placeholder files!")
    print("\\nNext steps:")
    print("1. Edit each generated file to implement specific elements")
    print("2. Update insert_all.py to include the new inserters")
    print("3. Update __init__.py to export the new classes")
    print("\\nFiles created:")
    for tenant_type in REMAINING_TENANTS:
        tenant_name = tenant_type.value
        file_name = f"tenant_{tenant_name}_elements.py"
        print(f"  - {file_name}")


if __name__ == "__main__":
    main() 