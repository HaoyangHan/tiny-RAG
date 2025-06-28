"""
Tenant Data Insertion Package for TinyRAG v1.4.

This package provides tools and scripts for manually inserting predefined
elements into the MongoDB database for different tenant types.

Available tenant inserters:
- HRElementInserter: Human Resources elements
- CodingElementInserter: Software development elements  
- FinancialElementInserter: Financial reporting elements

Usage:
    from tenant_data_insertion import MasterElementInserter
    from tenant_data_insertion.config import TenantType
    
    # Insert elements for all tenants
    inserter = MasterElementInserter()
    await inserter.run_all_parallel()
    
    # Insert elements for specific tenant
    inserter = MasterElementInserter([TenantType.HR])
    await inserter.run_all_sequential()
"""

from .base_inserter import BaseElementInserter, run_inserter
from .tenant_hr_elements import HRElementInserter
from .tenant_coding_elements import CodingElementInserter
from .tenant_financial_elements import FinancialElementInserter
from .insert_all import MasterElementInserter

__version__ = "1.4.0"
__author__ = "TinyRAG Team"

__all__ = [
    "BaseElementInserter",
    "run_inserter", 
    "HRElementInserter",
    "CodingElementInserter",
    "FinancialElementInserter",
    "MasterElementInserter"
] 