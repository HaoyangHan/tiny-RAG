"""
Financial Element Templates for TinyRAG v1.4.2
Updated for simplified chunk-based generation (July 2025)

This module contains the updated financial element templates that work with
the new simplified generation flow: retrieval chunks + optional additional instructions.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from models.enums import TenantType, TaskType, ElementType
from scripts.tenant_data_insertion.base_inserter import BaseElementTemplateInserter, run_template_inserter


class FinancialElementTemplateInserterV2(BaseElementTemplateInserter):
    """Updated financial element template inserter without variables."""
    
    def get_templates_data(self) -> List[Dict[str, Any]]:
        """Get financial element templates data using the new chunk-based approach."""
        
        return [
            # 1. Client Overview
            {
                "name": "RAG_Memo_Client_Overview",
                "description": "Generates the 'Client Overview' section of an investment memo, describing the company's business model, products, and market.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a financial analyst summarizing a company for an investment memo. Your task is to write the 'Client Overview' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, describe the company's core business model.
2. Detail its main products, services, and revenue streams.
3. Summarize its market position, key geographies, and primary customer base.
4. Do not infer information or use outside knowledge. Cite facts directly from the provided context.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Client Overview' Section:**""",
                "retrieval_prompt": "Information describing the company's business model, products, services, market position, and customers from the 'Business' section of its financial filings.",
                "additional_instructions_template": "Focus areas: [e.g., emphasize geographic diversity, highlight key products, focus on market leadership, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "client_overview", "business_description"]),
                "version": "2.0.0"
            },
            
            # 2. Historical Financial Analysis
            {
                "name": "RAG_Memo_Historical_Financial_Analysis",
                "description": "Generates a summary of historical financial performance, focusing on trends in revenue, profitability, and cash flow.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a credit analyst evaluating a company's financial history. Your task is to write the 'Historical Financial Analysis' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, analyze the key trends in revenue, EBITDA, and net income over the last 3 years.
2. Summarize the cash flow from operations, investing, and financing activities.
3. Identify and explain the primary drivers for these trends as mentioned in the Management's Discussion and Analysis (MD&A).
4. Present the information clearly and concisely.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Historical Financial Analysis' Section:**""",
                "retrieval_prompt": "Historical financial performance data, including revenue, EBITDA, net income, and cash flow trends from the MD&A and Selected Financial Data sections.",
                "additional_instructions_template": "Analysis focus: [e.g., emphasize cash flow trends, focus on margin analysis, highlight growth drivers, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2500
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "financial_analysis", "mda"]),
                "version": "2.0.0"
            },
            
            # 3. Liquidity Analysis
            {
                "name": "RAG_Memo_Liquidity_Analysis",
                "description": "Generates the 'Liquidity Analysis' section, assessing the company's ability to meet short-term obligations.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a credit analyst focused on liquidity risk. Your task is to write the 'Liquidity Analysis' section.

**Instructions:**
1. Using ONLY the retrieved document chunks below, assess the company's liquidity position.
2. Extract and discuss key metrics like cash and cash equivalents, working capital, and current ratio if available.
3. Summarize the company's primary sources of liquidity (e.g., cash from operations, revolving credit facilities).
4. Mention any discussion of liquidity challenges or strategies from the source text.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Liquidity Analysis' Section:**""",
                "retrieval_prompt": "Information regarding liquidity, capital resources, cash position, working capital, current ratio, and revolving credit facilities from financial filings.",
                "additional_instructions_template": "Liquidity focus: [e.g., emphasize cash conversion cycle, focus on credit facilities, highlight seasonal patterns, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "liquidity", "balance_sheet"]),
                "version": "2.0.0"
            },
            
            # 4. Leverage Analysis
            {
                "name": "RAG_Memo_Leverage_Analysis",
                "description": "Generates the 'Leverage' section, analyzing the company's debt levels and capital structure.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a credit analyst evaluating a company's debt burden. Your task is to write the 'Leverage' section.

**Instructions:**
1. From the retrieved document chunks below, identify the company's total debt and describe its capital structure (e.g., breakdown of senior secured, unsecured notes, etc.).
2. If available, state the company's leverage ratio (e.g., Debt-to-EBITDA).
3. Summarize any commentary on the company's leverage policy or debt management strategy.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Leverage' Section:**""",
                "retrieval_prompt": "Information about debt structure, leverage ratios, total debt, and capital structure from the MD&A section and debt footnote.",
                "additional_instructions_template": "Leverage focus: [e.g., emphasize debt covenant compliance, focus on leverage trajectory, highlight refinancing capacity, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "leverage", "debt_structure"]),
                "version": "2.0.0"
            },
            
            # 5. Stock Price Analysis
            {
                "name": "RAG_Memo_Stock_Price_Analysis",
                "description": "Generates the 'Stock Price Analysis' section, analyzing stock performance from recent disclosures.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a market analyst. Your task is to provide a brief 'Stock Price Analysis' based on the company's own disclosures.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, summarize the company's description of its stock performance.
2. Mention the exchange it trades on and its ticker symbol.
3. If the context includes a stock performance graph or comparison to an index (like the S&P 500), describe it.
4. Note any information on dividend policy or stock repurchase programs.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Stock Price Analysis' Section:**""",
                "retrieval_prompt": "Stock performance information, trading data, dividend policy, and share repurchase programs from financial disclosures.",
                "additional_instructions_template": "Stock analysis focus: [e.g., emphasize dividend sustainability, focus on share buyback impact, highlight trading volume patterns, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "stock_price", "market_analysis"]),
                "version": "2.0.0"
            },
            
            # 6. ESG Analysis
            {
                "name": "RAG_Memo_ESG_Analysis",
                "description": "Generates an 'ESG Analysis' section, summarizing environmental, social, and governance factors.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are an ESG analyst. Your task is to write an 'ESG Analysis' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, summarize the company's environmental, social, and governance initiatives.
2. Highlight any ESG risks or challenges mentioned in the disclosures.
3. Note any ESG ratings, certifications, or sustainability goals discussed.
4. Keep the analysis balanced and fact-based.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'ESG Analysis' Section:**""",
                "retrieval_prompt": "ESG information, sustainability initiatives, governance practices, and environmental policies from corporate disclosures.",
                "additional_instructions_template": "ESG focus: [e.g., emphasize climate risk disclosures, focus on diversity metrics, highlight governance changes, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "esg", "sustainability"]),
                "version": "2.0.0"
            },
            
            # 7. Risk Factors Analysis
            {
                "name": "RAG_Memo_Risk_Factors_Analysis",
                "description": "Generates a 'Risk Factors Analysis' section, summarizing key business and financial risks.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are a risk analyst. Your task is to write a 'Risk Factors Analysis' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, identify and summarize the most significant business and financial risks.
2. Group risks by category (e.g., operational, market, financial, regulatory).
3. Prioritize risks based on their potential impact as described in the source documents.
4. Avoid speculation; stick to risks explicitly mentioned by the company.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Risk Factors Analysis' Section:**""",
                "retrieval_prompt": "Risk factor disclosures, business risks, financial risks, and regulatory risks from the 'Risk Factors' section of financial filings.",
                "additional_instructions_template": "Risk focus: [e.g., emphasize operational risks, focus on regulatory changes, highlight market risks, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2500
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "risk_factors", "business_risks"]),
                "version": "2.0.0"
            },
            
            # 8. Management Assessment
            {
                "name": "RAG_Memo_Management_Assessment",
                "description": "Generates a 'Management Assessment' section, evaluating leadership and strategic direction.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are analyzing corporate management for investment purposes. Your task is to write a 'Management Assessment' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, summarize key management team members and their backgrounds.
2. Note any recent management changes or succession planning discussed.
3. Highlight strategic initiatives or major decisions mentioned in management commentary.
4. Keep the assessment professional and fact-based.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Management Assessment' Section:**""",
                "retrieval_prompt": "Management biographies, executive compensation, strategic initiatives, and management commentary from proxy statements and MD&A sections.",
                "additional_instructions_template": "Management focus: [e.g., emphasize leadership experience, focus on strategic vision, highlight succession planning, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "management", "leadership"]),
                "version": "2.0.0"
            },
            
            # 9. Industry Analysis
            {
                "name": "RAG_Memo_Industry_Analysis",
                "description": "Generates an 'Industry Analysis' section, providing context on the company's operating environment.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are an industry analyst. Your task is to write an 'Industry Analysis' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, summarize the company's description of its industry and competitive environment.
2. Note any industry trends, challenges, or opportunities mentioned by the company.
3. Highlight the company's competitive positioning as described in the source materials.
4. Avoid external industry knowledge; focus on company disclosures.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Industry Analysis' Section:**""",
                "retrieval_prompt": "Industry descriptions, competitive landscape analysis, market trends, and business environment discussions from company filings.",
                "additional_instructions_template": "Industry focus: [e.g., emphasize competitive advantages, focus on market trends, highlight regulatory environment, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "industry", "competitive_analysis"]),
                "version": "2.0.0"
            },
            
            # 10. Financial Projections Summary
            {
                "name": "RAG_Memo_Financial_Projections_Summary",
                "description": "Generates a 'Financial Projections Summary' section based on forward-looking statements.",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "generation_prompt": """You are summarizing forward-looking financial information. Your task is to write a 'Financial Projections Summary' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, summarize any forward-looking financial guidance or projections provided by the company.
2. Note any assumptions or conditions mentioned for these projections.
3. Highlight key metrics or targets mentioned (revenue growth, margin expectations, capex guidance, etc.).
4. Include appropriate caveats about forward-looking statements.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Financial Projections Summary' Section:**""",
                "retrieval_prompt": "Forward-looking statements, financial guidance, business outlook, and management projections from earnings calls and forward-looking disclosure sections.",
                "additional_instructions_template": "Projections focus: [e.g., emphasize growth targets, focus on margin guidance, highlight capital allocation plans, etc.]",
                "execution_config": {
                    "model": "gpt-4-turbo",
                    "temperature": 0.2,
                    "max_tokens": 2000
                },
                "tags": self.create_element_tags(["finance", "rag", "memo", "projections", "forward_looking"]),
                "version": "2.0.0"
            }
        ]


async def main():
    """Main function to insert financial element templates."""
    result = await run_template_inserter(
        FinancialElementTemplateInserterV2,
        TenantType.FINANCIAL_REPORT
    )
    
    print("\n" + "="*60)
    print("FINANCIAL REPORT V2 ELEMENT TEMPLATE INSERTION SUMMARY")
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


    