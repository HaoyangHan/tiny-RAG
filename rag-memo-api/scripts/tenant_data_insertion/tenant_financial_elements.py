"""
Financial Report Tenant Element Insertion Script.

This script contains predefined elements for Financial Report tenant type, including
RAG-based investment memo workflows for financial analysis and reporting automation.
"""

import asyncio
from typing import List, Dict, Any

from models.enums import TenantType, TaskType, ElementType, ElementStatus
from .base_inserter import BaseElementInserter


class FinancialElementInserter(BaseElementInserter):
    """Element inserter for Financial Report tenant type with RAG-based investment memo templates."""
    
    def get_elements_data(self) -> List[Dict[str, Any]]:
        """
        Get predefined Financial Report RAG investment memo elements.
        
        Returns:
            List[Dict[str, Any]]: List of Financial Report element data
        """
        return [
            # 1. Client Overview
            {
                "name": "RAG_Memo_Client_Overview",
                "description": "Generates the 'Client Overview' section of an investment memo, describing the company's business model, products, and market.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a financial analyst summarizing a company for an investment memo. Your task is to write the 'Client Overview' section.

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
                    generation_prompt="""You are a financial analyst summarizing a company for an investment memo. Your task is to write the 'Client Overview' section.

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
                    retrieval_prompt="Information describing {company_name}'s business model, products, services, market position, and customers from the 'Business' section of its financial filings.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.2,
                        "max_tokens": 2000
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "client_overview", "business_description"])
            },
            
            # 2. Historical Financial Analysis
            {
                "name": "RAG_Memo_Historical_Financial_Analysis",
                "description": "Generates a summary of historical financial performance, focusing on trends in revenue, profitability, and cash flow.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a credit analyst evaluating a company's financial history. Your task is to write the 'Historical Financial Analysis' section.

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
                    generation_prompt="""You are a credit analyst evaluating a company's financial history. Your task is to write the 'Historical Financial Analysis' section.

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
                    retrieval_prompt="Historical financial performance data, including revenue, EBITDA, net income, and cash flow trends for {company_name} from the MD&A and Selected Financial Data sections.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.2,
                        "max_tokens": 2500
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "financial_analysis", "mda"])
            },
            
            # 3. Liquidity Analysis
            {
                "name": "RAG_Memo_Liquidity_Analysis",
                "description": "Generates the 'Liquidity Analysis' section, assessing the company's ability to meet short-term obligations.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a credit analyst focused on liquidity risk. Your task is to write the 'Liquidity Analysis' section.

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
                    generation_prompt="""You are a credit analyst focused on liquidity risk. Your task is to write the 'Liquidity Analysis' section.

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
                    retrieval_prompt="Information regarding {company_name}'s liquidity, capital resources, cash position, working capital, current ratio, and revolving credit facilities from its financial filings.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.1,
                        "max_tokens": 2000
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "liquidity", "balance_sheet"])
            },
            
            # 4. Leverage Analysis
            {
                "name": "RAG_Memo_Leverage_Analysis",
                "description": "Generates the 'Leverage' section, analyzing the company's debt levels and capital structure.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a credit analyst evaluating a company's debt burden. Your task is to write the 'Leverage' section.

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
                    generation_prompt="""You are a credit analyst evaluating a company's debt burden. Your task is to write the 'Leverage' section.

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
                    retrieval_prompt="Details on {company_name}'s total debt, capital structure, leverage ratios, credit facilities, and notes from balance sheets and debt footnotes.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.1,
                        "max_tokens": 2000
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "leverage", "debt", "capital_structure"])
            },
            
            # 5. Refinancing Risks
            {
                "name": "RAG_Memo_Refinancing_Risks",
                "description": "Generates the 'Refinancing Risks' section, highlighting risks associated with upcoming debt maturities.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a financial risk analyst. Your task is to write the 'Refinancing Risks' section based on the provided context.

**Instructions:**
1.  Identify any near-term debt maturities mentioned in the `source_documents`.
2.  Summarize the company's stated ability or plans to refinance this debt.
3.  Highlight any discussed risks related to refinancing, such as access to capital markets, interest rate risk, or credit rating concerns.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Refinancing Risks' Section:**""",
                    generation_prompt="""You are a financial risk analyst. Your task is to write the 'Refinancing Risks' section based on the provided context.

**Instructions:**
1.  Identify any near-term debt maturities mentioned in the `source_documents`.
2.  Summarize the company's stated ability or plans to refinance this debt.
3.  Highlight any discussed risks related to refinancing, such as access to capital markets, interest rate risk, or credit rating concerns.

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Refinancing Risks' Section:**""",
                    retrieval_prompt="Information about {company_name}'s upcoming debt maturities, refinancing plans, access to capital markets, and associated risks.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.2,
                        "max_tokens": 2000
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "risk", "refinancing", "debt"])
            },
            
            # 6. Debt Maturity Schedule
            {
                "name": "RAG_Memo_Debt_Maturity_Schedule",
                "description": "Extracts and formats the company's debt maturity schedule into a clear table.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a data extraction specialist. Your task is to create a 'Debt Maturity Schedule' in a Markdown table format.

**Instructions:**
1.  Scan the provided `source_documents` for a table or list of contractual obligations or debt maturities.
2.  Extract the different debt tranches, their outstanding amounts, and their respective maturity years.
3.  Format this information into a clean Markdown table with columns: 'Debt Facility/Note', 'Amount Outstanding', and 'Maturity Year'.
4.  If no specific schedule is found, state "A detailed debt maturity schedule was not found in the provided context."

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Debt Maturity Schedule' Section:**""",
                    generation_prompt="""You are a data extraction specialist. Your task is to create a 'Debt Maturity Schedule' in a Markdown table format.

**Instructions:**
1.  Scan the provided `source_documents` for a table or list of contractual obligations or debt maturities.
2.  Extract the different debt tranches, their outstanding amounts, and their respective maturity years.
3.  Format this information into a clean Markdown table with columns: 'Debt Facility/Note', 'Amount Outstanding', and 'Maturity Year'.
4.  If no specific schedule is found, state "A detailed debt maturity schedule was not found in the provided context."

**Company:** {company_name}

**Source Documents (Context):**
---
{source_documents}
---

**Generated 'Debt Maturity Schedule' Section:**""",
                    retrieval_prompt="Tables or text detailing {company_name}'s contractual obligations, debt maturities, and future payment schedules from financial footnotes.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.0,
                        "max_tokens": 1500
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "debt_maturity", "schedule", "extraction"])
            },
            
            # 7. Facility Request
            {
                "name": "RAG_Memo_Facility_Request",
                "description": "Summarizes the details of the new loan or facility being requested.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are an analyst summarizing a deal term sheet. Your task is to write the 'Facility Request' section.

**Instructions:**
1.  The `source_documents` for this task will likely be a specific term sheet or prospectus.
2.  From this context, describe the proposed transaction.
3.  Specify the requested amount, the type of facility (e.g., Senior Secured Term Loan), the proposed term/maturity, and pricing (if available).
4.  Clearly state the 'Use of Proceeds' (e.g., refinancing existing debt, funding an acquisition).

**Company:** {company_name}

**Source Documents (Context from Term Sheet/Prospectus):**
---
{source_documents}
---

**Generated 'Facility Request' Section:**""",
                    generation_prompt="""You are an analyst summarizing a deal term sheet. Your task is to write the 'Facility Request' section.

**Instructions:**
1.  The `source_documents` for this task will likely be a specific term sheet or prospectus.
2.  From this context, describe the proposed transaction.
3.  Specify the requested amount, the type of facility (e.g., Senior Secured Term Loan), the proposed term/maturity, and pricing (if available).
4.  Clearly state the 'Use of Proceeds' (e.g., refinancing existing debt, funding an acquisition).

**Company:** {company_name}

**Source Documents (Context from Term Sheet/Prospectus):**
---
{source_documents}
---

**Generated 'Facility Request' Section:**""",
                    retrieval_prompt="Details of the proposed transaction for {company_name}, including loan amount, purpose, use of proceeds, term, and pricing from a prospectus or deal term sheet.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.1,
                        "max_tokens": 2000
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "facility_request", "term_sheet", "prospectus"])
            },
            
            # 8. Obligor Assessment
            {
                "name": "RAG_Memo_Obligor_Assessment",
                "description": "Describes the legal entity borrowing the money and its relationship within the corporate structure.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a legal and financial analyst. Your task is to write the 'Obligor Assessment' section.

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
                    generation_prompt="""You are a legal and financial analyst. Your task is to write the 'Obligor Assessment' section.

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
                    retrieval_prompt="Information on the corporate structure of {company_name}, including subsidiaries, parent company guarantees, and the specific legal entities acting as obligors.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.2,
                        "max_tokens": 1800
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "obligor", "guarantor", "legal"])
            },
            
            # 9. Key Risks
            {
                "name": "RAG_Memo_Key_Risks",
                "description": "Summarizes the most critical risks to the business and creditworthiness.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a risk analyst. Your task is to write the 'Key Risks' section, summarizing the most critical risks.

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
                    generation_prompt="""You are a risk analyst. Your task is to write the 'Key Risks' section, summarizing the most critical risks.

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
                    retrieval_prompt="The 'Risk Factors' section from {company_name}'s 10-K and other filings, detailing risks to the business.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.3,
                        "max_tokens": 2500
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "risk_factors", "credit_risk"])
            },
            
            # 10. Stock Price Analysis
            {
                "name": "RAG_Memo_Stock_Price_Analysis",
                "description": "Generates a summary of the company's stock performance.",
                "task_type": TaskType.RAG_QA,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""You are a market analyst. Your task is to provide a brief 'Stock Price Analysis' based on the company's own disclosures.

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
                    generation_prompt="""You are a market analyst. Your task is to provide a brief 'Stock Price Analysis' based on the company's own disclosures.

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
                    retrieval_prompt="Information regarding {company_name}'s stock performance, stock ticker, trading market, and comparison to market indices from the 'Market for Registrant's Common Equity' section.",
                    variables=["company_name", "source_documents"],
                    execution_config={
                        "model": "gpt-4-turbo",
                        "temperature": 0.2,
                        "max_tokens": 2000
                    }
                ),
                "tags": self.create_element_tags(["finance", "rag", "memo", "stock_price", "market_analysis"])
            }
        ]


async def main():
    """Main function to run Financial Report RAG element insertion."""
    inserter = FinancialElementInserter(TenantType.FINANCIAL_REPORT)
    result = await inserter.run()
    
    print("\n" + "="*60)
    print("FINANCIAL REPORT RAG ELEMENT INSERTION SUMMARY")
    print("="*60)
    print(f"Tenant Type: {result.get('tenant_type', 'Unknown')}")
    print(f"Total Elements: {result.get('total_elements', 0)}")
    print(f"Successful: {result.get('successful', 0)}")
    print(f"Failed: {result.get('failed', 0)}")
    print(f"Skipped: {result.get('skipped', 0)}")
    print(f"Dry Run: {result.get('dry_run', False)}")
    
    if result.get('inserted_ids'):
        print(f"\nInserted Element IDs:")
        for element_id in result['inserted_ids']:
            print(f"  - {element_id}")
    
    if result.get('error'):
        print(f"\nError: {result['error']}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main()) 