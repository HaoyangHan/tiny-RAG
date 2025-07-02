#!/usr/bin/env python3
"""
Simple debug script to test database queries directly.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from models.enums import TenantType, ElementStatus
from database import get_database_url
from models.element_template import ElementTemplate as StandaloneElementTemplate
import motor.motor_asyncio
from beanie import init_beanie


async def simple_debug():
    """Simple debug test."""
    print("=== SIMPLE DATABASE DEBUG ===")
    
    # Connect to database
    client = motor.motor_asyncio.AsyncIOMotorClient(get_database_url())
    database = client["tinyrag"]
    
    # Initialize Beanie
    await init_beanie(
        database=database,
        document_models=[StandaloneElementTemplate]
    )
    
    # Test values
    tenant_type = TenantType.FINANCIAL_REPORT
    print(f"TenantType.FINANCIAL_REPORT.value = '{tenant_type.value}'")
    print(f"ElementStatus.ACTIVE.value = '{ElementStatus.ACTIVE.value}'")
    
    # Test 1: Raw MongoDB query
    collection = database.element_templates
    count_raw = await collection.count_documents({"tenant_type": "financial_report"})
    print(f"Raw MongoDB count: {count_raw}")
    
    # Test 2: Simple Beanie query
    templates = await StandaloneElementTemplate.find({
        "tenant_type": tenant_type.value
    }).to_list()
    print(f"Beanie simple query found: {len(templates)} templates")
    
    # Test 3: Full query with status
    query = {
        "tenant_type": tenant_type.value,
        "$or": [
            {"status": ElementStatus.ACTIVE.value},
            {"status": {"$exists": False}}
        ]
    }
    print(f"Full query: {query}")
    templates_full = await StandaloneElementTemplate.find(query).to_list()
    print(f"Full query found: {len(templates_full)} templates")
    
    if templates_full:
        print("First template:")
        template = templates_full[0]
        print(f"  Name: {template.name}")
        print(f"  Tenant Type: {template.tenant_type}")
        print(f"  Status: {getattr(template, 'status', 'MISSING')}")
    
    # Clean up
    client.close()
    print("=== DEBUG COMPLETE ===")


if __name__ == "__main__":
    asyncio.run(simple_debug()) 