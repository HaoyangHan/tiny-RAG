#!/usr/bin/env python3
"""
Update Element Template Models Script for TinyRAG v1.4.2
Updates existing element templates and elements in MongoDB to use supported LLM model.
"""

import asyncio
import os
import sys
from typing import List, Dict, Any
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database, get_database_url
from models.element_template import ElementTemplate
from models.element import Element
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient


async def update_element_template_models():
    """Update all element templates to use supported LLM model."""
    
    try:
        # Initialize database connection
        database_url = get_database_url()
        print(f"🔌 Connecting to MongoDB: {database_url}")
        
        client = AsyncIOMotorClient(database_url)
        database = client.tinyrag
        
        # Initialize Beanie with both ElementTemplate and Element models
        await init_beanie(database=database, document_models=[ElementTemplate, Element])
        
        print("✅ Database connection established")
        
        # Find all element templates with gpt-4-turbo model
        print("🔍 Finding element templates with gpt-4-turbo model...")
        
        templates = await ElementTemplate.find({
            "execution_config.model": "gpt-4-turbo"
        }).to_list()
        
        print(f"📊 Found {len(templates)} templates to update")
        
        # Update each template
        updated_template_count = 0
        for template in templates:
            try:
                # Update the model in execution_config
                if hasattr(template, 'execution_config') and template.execution_config:
                    if isinstance(template.execution_config, dict):
                        template.execution_config['model'] = "gpt-4.1-nano-2025-04-14"
                    else:
                        # If it's a Pydantic model with model attribute
                        template.execution_config.model = "gpt-4.1-nano-2025-04-14"
                    
                    # Update timestamp
                    template.updated_at = datetime.utcnow()
                    
                    # Save the template
                    await template.save()
                    
                    print(f"✅ Updated template: {template.name}")
                    updated_template_count += 1
                    
            except Exception as e:
                print(f"❌ Failed to update template {template.name}: {e}")
        
        # Find all elements with gpt-4-turbo model
        print("\n🔍 Finding elements with gpt-4-turbo model...")
        
        elements = await Element.find({
            "template.execution_config.model": "gpt-4-turbo"
        }).to_list()
        
        print(f"📊 Found {len(elements)} elements to update")
        
        # Update each element
        updated_element_count = 0
        for element in elements:
            try:
                # Update the model in element template execution_config
                if hasattr(element, 'template') and element.template and element.template.execution_config:
                    if isinstance(element.template.execution_config, dict):
                        element.template.execution_config['model'] = "gpt-4.1-nano-2025-04-14"
                    else:
                        # If it's a Pydantic model with model attribute
                        element.template.execution_config.model = "gpt-4.1-nano-2025-04-14"
                    
                    # Update timestamp
                    element.updated_at = datetime.utcnow()
                    
                    # Save the element
                    await element.save()
                    
                    print(f"✅ Updated element: {element.name}")
                    updated_element_count += 1
                    
            except Exception as e:
                print(f"❌ Failed to update element {element.name}: {e}")
        
        print(f"\n🎉 Successfully updated {updated_template_count} element templates and {updated_element_count} elements")
        print(f"   Model changed from: gpt-4-turbo")
        print(f"   Model changed to:   gpt-4.1-nano-2025-04-14")
        
        # Verify the changes
        print("\n🔍 Verifying updates...")
        remaining_old_template_models = await ElementTemplate.find({
            "execution_config.model": "gpt-4-turbo"
        }).count()
        
        remaining_old_element_models = await Element.find({
            "template.execution_config.model": "gpt-4-turbo"
        }).count()
        
        new_template_models = await ElementTemplate.find({
            "execution_config.model": "gpt-4.1-nano-2025-04-14"
        }).count()
        
        new_element_models = await Element.find({
            "template.execution_config.model": "gpt-4.1-nano-2025-04-14"
        }).count()
        
        print(f"   Templates still using gpt-4-turbo: {remaining_old_template_models}")
        print(f"   Elements still using gpt-4-turbo: {remaining_old_element_models}")
        print(f"   Templates now using gpt-4.1-nano-2025-04-14: {new_template_models}")
        print(f"   Elements now using gpt-4.1-nano-2025-04-14: {new_element_models}")
        
        if remaining_old_template_models == 0 and remaining_old_element_models == 0:
            print("✅ All templates and elements successfully updated!")
        else:
            print("⚠️  Some templates or elements may need manual review")
            
    except Exception as e:
        print(f"❌ Error updating element templates and elements: {e}")
        raise
    finally:
        if 'client' in locals():
            client.close()


async def main():
    """Main function to run the update script."""
    print("🚀 TinyRAG Element Template and Element Model Update Script")
    print("=" * 60)
    print("📝 Updating element templates and elements to use supported LLM model")
    print("   From: gpt-4-turbo")
    print("   To:   gpt-4.1-nano-2025-04-14")
    print()
    
    try:
        await update_element_template_models()
        print("\n✅ Update process completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Update process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 