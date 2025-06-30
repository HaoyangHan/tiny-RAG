"""
Tenant Data Insertion Package for TinyRAG v1.4.2.

This package provides tools and scripts for manually inserting predefined
element templates into the MongoDB database for different tenant types.

Available tenant template inserters:
- HRElementInserter: Human Resources elements (legacy)
- CodingElementInserter: Software development elements (legacy)
- FinancialElementTemplateInserter: Financial reporting element templates
- BaseElementTemplateInserter: New template-based inserter

Usage:
    from tenant_data_insertion import run_template_inserter
    from tenant_data_insertion.tenant_financial_elements import FinancialElementTemplateInserter
    from models.enums import TenantType
    
    # Insert templates for financial tenant
    result = await run_template_inserter(
        FinancialElementTemplateInserter,
        TenantType.FINANCIAL_REPORT
    )
"""

from .base_inserter import BaseElementInserter, BaseElementTemplateInserter, run_inserter, run_template_inserter
from .tenant_hr_elements import HRElementInserter
from .tenant_coding_elements import CodingElementInserter
from .tenant_financial_elements import FinancialElementTemplateInserter
from .insert_all import MasterElementInserter

__version__ = "1.4.2"
__author__ = "TinyRAG Team"

__all__ = [
    "BaseElementInserter",
    "BaseElementTemplateInserter",
    "run_inserter",
    "run_template_inserter",
    "HRElementInserter",
    "CodingElementInserter",
    "FinancialElementTemplateInserter",
    "MasterElementInserter"
] 