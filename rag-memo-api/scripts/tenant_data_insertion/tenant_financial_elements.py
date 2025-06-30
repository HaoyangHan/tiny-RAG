"""
Financial Report Tenant Element Template Insertion Script.

This script contains predefined element templates for Financial Report tenant type, including
RAG-based investment memo workflows for financial analysis and reporting automation.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from models.enums import TenantType, TaskType, ElementType, ElementStatus
from scripts.tenant_data_insertion.base_inserter import BaseElementTemplateInserter, run_template_inserter


class FinancialElementTemplateInserter(BaseElementTemplateInserter):
    """Element template inserter for Financial Report tenant type with RAG-based investment memo templates."""
    
    def get_templates_data(self) -> List[Dict[str, Any]]:
        """
        Get predefined Financial Report RAG investment memo element templates.
        
        Returns:
            List[Dict[str, Any]]: List of Financial Report template data
        """
        return [
            # 1. Client Overview
            {
                "name": "RAG_Memo_Client_Overview",
                "description": "Generates the 'Client Overview' section of an investment memo, describing the company's business model, products, and market.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a financial analyst summarizing a company for an investment memo. Your task is to write the 'Client Overview' section.

**Instructions:**
1.  Based ONLY on the provided `source_documents`, describe the company's core business model.
2.  Detail its main products, services, and revenue streams.
3.  Summarize its market position, key geographies, and primary customer base.
4.  Do not infer information or use outside knowledge. Cite facts directly from the provided context.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Client Overview' Section:**""",
                "retrieval_prompt": "Information describing {company_name}'s business model, products, services, market position, and customers from the 'Business' section of its financial filings.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "client_overview", "business_description"]),
                "version": "1.0.0"
            },
            
            # 2. Historical Financial Analysis
            {
                "name": "RAG_Memo_Historical_Financial_Analysis",
                "description": "Generates a summary of historical financial performance, focusing on trends in revenue, profitability, and cash flow.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a credit analyst evaluating a company's financial history. Your task is to write the 'Historical Financial Analysis' section.

**Instructions:**
1.  Based ONLY on the provided `source_documents`, analyze the key trends in revenue, EBITDA, and net income over the last 3 years.
2.  Summarize the cash flow from operations, investing, and financing activities.
3.  Identify and explain the primary drivers for these trends as mentioned in the Management's Discussion and Analysis (MD&A).
4.  Present the information clearly and concisely.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Historical Financial Analysis' Section:**""",
                "retrieval_prompt": "Historical financial performance data, including revenue, EBITDA, net income, and cash flow trends for {company_name} from the MD&A and Selected Financial Data sections.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2500
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "financial_analysis", "mda"]),
                "version": "1.0.0"
            },
            
            # 3. Liquidity Analysis
            {
                "name": "RAG_Memo_Liquidity_Analysis",
                "description": "Generates the 'Liquidity Analysis' section, assessing the company's ability to meet short-term obligations.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a credit analyst focused on liquidity risk. Your task is to write the 'Liquidity Analysis' section.

**Instructions:**
1.  Using ONLY the provided `source_documents`, assess the company's liquidity position.
2.  Extract and discuss key metrics like cash and cash equivalents, working capital, and current ratio if available.
3.  Summarize the company's primary sources of liquidity (e.g., cash from operations, revolving credit facilities).
4.  Mention any discussion of liquidity challenges or strategies from the source text.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Liquidity Analysis' Section:**""",
                "retrieval_prompt": "Information regarding {company_name}'s liquidity, capital resources, cash position, working capital, current ratio, and revolving credit facilities from its financial filings.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "liquidity", "balance_sheet"]),
                "version": "1.0.0"
            },
            
            # 4. Leverage Analysis
            {
                "name": "RAG_Memo_Leverage_Analysis",
                "description": "Generates the 'Leverage' section, analyzing the company's debt levels and capital structure.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a credit analyst evaluating a company's debt burden. Your task is to write the 'Leverage' section.

**Instructions:**
1.  From the provided `source_documents`, identify the company's total debt and describe its capital structure (e.g., breakdown of senior secured, unsecured notes, etc.).
2.  If available, state the company's leverage ratio (e.g., Debt-to-EBITDA).
3.  Summarize any commentary on the company's leverage policy or debt management strategy.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Leverage' Section:**""",
                "retrieval_prompt": "Information about {company_name}'s debt structure, leverage ratios, total debt, and capital structure from the MD&A section and debt footnote.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "leverage", "debt_structure"]),
                "version": "1.0.0"
            },
            
            # 5. Refinancing Risks
            {
                "name": "RAG_Memo_Refinancing_Risks",
                "description": "Generates the 'Refinancing Risks' section, analyzing near-term debt maturities and refinancing pressures.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a credit analyst focused on refinancing risk. Your task is to write the 'Refinancing Risks' section.

**Instructions:**
1.  Based on the provided `source_documents`, identify debt maturities over the next 3-5 years.
2.  Assess the magnitude of refinancing needs relative to the company's size.
3.  Mention any commentary from management about refinancing plans or market access.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Refinancing Risks' Section:**""",
                "retrieval_prompt": "Information about debt maturity schedule, upcoming refinancing needs, and management commentary on future financing plans for {company_name}.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.1,
                    "max_tokens": 1800
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "refinancing_risk", "debt_maturity"]),
                "version": "1.0.0"
            },
            
            # 6. Debt Maturity Schedule
            {
                "name": "RAG_Memo_Debt_Maturity_Schedule",
                "description": "Generates the 'Debt Maturity Schedule' section with a tabular breakdown of debt obligations.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a financial analyst creating a debt maturity schedule. Your task is to write the 'Debt Maturity Schedule' section.

**Instructions:**
1.  From the provided `source_documents`, extract details about the maturity dates and amounts of the company's debt.
2.  Present this information in a clear, tabular format if possible.
3.  Include details like facility type, maturity date, amount outstanding, and interest rate where available.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Debt Maturity Schedule' Section:**""",
                "retrieval_prompt": "Detailed debt maturity information for {company_name}, including facility types, amounts, maturity dates, and interest rates from the debt footnote and financing sections.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "debt_schedule", "maturity_profile"]),
                "version": "1.0.0"
            },
            
            # 7. Facility Request
            {
                "name": "RAG_Memo_Facility_Request",
                "description": "Generates the 'Facility Request' section, outlining the terms of the proposed financing facility.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a deal originator documenting a proposed transaction. Your task is to write the 'Facility Request' section.

**Instructions:**
1.  Based on the provided `source_documents` (term sheet, prospectus, etc.), detail the proposed facility amount, purpose, and use of proceeds.
2.  Mention the term/maturity, pricing (if available), and any key covenants or terms.
3.  Describe how the proposed facility fits into the borrower's overall capital structure.

**Company:** {company_name}

**Source Documents (Context from Term Sheet/Prospectus):**
---
{source_documents}
---

**Generated 'Facility Request' Section:**""",
                "retrieval_prompt": "Details of the proposed transaction for {company_name}, including loan amount, purpose, use of proceeds, term, and pricing from a prospectus or deal term sheet.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "facility_request", "term_sheet", "prospectus"]),
                "version": "1.0.0"
            },
            
            # 8. Obligor Assessment
            {
                "name": "RAG_Memo_Obligor_Assessment",
                "description": "Generates the 'Obligor Assessment' section, describing the legal entity and corporate structure.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a legal and financial analyst. Your task is to write the 'Obligor Assessment' section.

**Instructions:**
1.  Based on the `source_documents`, identify the specific legal entity (or entities) that will be the borrower/obligor for the proposed facility.
2.  Describe the obligor's position within the parent company's corporate structure.
3.  Mention any guarantees from the parent company or other subsidiaries, if described in the context.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Obligor Assessment' Section:**""",
                "retrieval_prompt": "Information on the corporate structure of {company_name}, including subsidiaries, parent company guarantees, and the specific legal entities acting as obligors.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 1800
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "obligor", "guarantor", "legal"]),
                "version": "1.0.0"
            },
            
            # 9. Key Risks
            {
                "name": "RAG_Memo_Key_Risks",
                "description": "Generates the 'Key Risks' section, extracting critical business and credit risks from 10-K filings.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a risk analyst. Your task is to write the 'Key Risks' section, summarizing the most critical risks.

**Instructions:**
1.  Review the `source_documents`, paying close attention to the 'Risk Factors' section of the 10-K.
2.  Synthesize and summarize the 3-5 most material risks to the company's business and financial stability.
3.  Categorize risks where possible (e.g., Operational, Market, Financial, Regulatory).
4.  Be concise and focus on the risks most relevant to a lender.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Key Risks' Section:**""",
                "retrieval_prompt": "The 'Risk Factors' section from {company_name}'s 10-K and other filings, detailing risks to the business.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.3,
                    "max_tokens": 2500
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "risk_factors", "credit_risk"]),
                "version": "1.0.0"
            },
            
            # 10. Stock Price Analysis
            {
                "name": "RAG_Memo_Stock_Price_Analysis",
                "description": "Generates the 'Stock Price Analysis' section, analyzing stock performance from recent disclosures.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a market analyst. Your task is to provide a brief 'Stock Price Analysis' based on the company's own disclosures.

**Instructions:**
1.  Based ONLY on the provided `source_documents`, summarize the company's description of its stock performance.
2.  Mention the exchange it trades on and its ticker symbol.
3.  If the context includes a stock performance graph or comparison to an index (like the S&P 500), describe it.
4.  Note any information on dividend policy or stock repurchase programs.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Stock Price Analysis' Section:**""",
                "retrieval_prompt": "Information regarding {company_name}'s stock performance, stock ticker, trading market, and comparison to market indices from the 'Market for Registrant's Common Equity' section.",
                "variables": ["company_name", "source_documents"],
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "stock_price", "market_analysis"]),
                "version": "1.0.0"
            }
        ]


async def main():
    """Main function to run Financial Report RAG element template insertion."""
    result = await run_template_inserter(
        FinancialElementTemplateInserter,
        TenantType.FINANCIAL_REPORT
    )
    
    print("\n" + "="*60)
    print("FINANCIAL REPORT RAG ELEMENT TEMPLATE INSERTION SUMMARY")
    print("="*60)
    print(f"Tenant Type: {result.get('tenant_type', 'Unknown')}")
    print(f"Total Templates: {result.get('total_templates', 0)}")
    print(f"Successful: {result.get('successful', 0)}")
    print(f"Failed: {result.get('failed', 0)}")
    print(f"Skipped: {result.get('skipped', 0)}")
    print(f"Dry Run: {result.get('dry_run', False)}")
    
    if result.get('inserted_ids'):
        print(f"\nInserted Template IDs:")
        for template_id in result['inserted_ids']:
            print(f"  - {template_id}")
    
    if result.get('error'):
        print(f"\nError: {result['error']}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main()) 