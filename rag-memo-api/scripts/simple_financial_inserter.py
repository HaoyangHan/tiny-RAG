#!/usr/bin/env python3
"""
Simple Financial Element Templates Inserter for TinyRAG v1.4.2
Bypasses complex insertion infrastructure to directly insert templates.
Complete set of 10 financial element templates (V2 - Chunk-based).
"""

import asyncio
import os
from typing import List, Dict, Any
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.enums import TenantType, TaskType, ElementType, ElementStatus
from models.element_template import ElementTemplate
from auth.models import User


async def insert_financial_templates_v2():
    """Insert updated financial element templates without variables - Complete set of 10 templates."""
    
    # Connect to database using environment variable
    mongodb_url = os.getenv('MONGODB_URL')
    print(f"🔗 Connecting to MongoDB: {mongodb_url}")
    
    client = AsyncIOMotorClient(mongodb_url)
    
    # Initialize Beanie with required models
    await init_beanie(
        database=client.tinyrag,
        document_models=[ElementTemplate, User]
    )
    
    print('🚀 Inserting Financial Element Templates V2 (Complete Set - 10 Templates)...')
    
    # Helper function to create tags
    def create_tags(specific_tags: List[str]) -> List[str]:
        common_tags = ['v1.4.2', 'system', 'template']
        tenant_prefix = 'finance'
        return list(set(common_tags + [tenant_prefix] + specific_tags))
    
    # Define financial templates data - Complete set of 10 templates
    default_user_id = "system"  # Default user ID for system templates
    
    templates_data = [
        # 1. Client Overview
        {
            'name': 'RAG_Memo_Client_Overview_V2',
            'description': 'Generates the Client Overview section using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a financial analyst summarizing a company for an investment memo. Your task is to write the 'Client Overview' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, describe the company's core business model.
2. Detail its main products, services, and revenue streams.
3. Summarize its market position, key geographies, and primary customer base.
4. Do not infer information or use outside knowledge. Cite facts directly from the provided context.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Client Overview' Section:**''',
            'retrieval_prompt': 'Information describing the company\'s business model, products, services, market position, and customers from financial filings.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.2,
                'max_tokens': 2000
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'client_overview', 'business_description']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 2. Historical Financial Analysis
        {
            'name': 'RAG_Memo_Financial_Analysis_V2',
            'description': 'Generates historical financial analysis using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a credit analyst evaluating a company's financial history. Your task is to write the 'Historical Financial Analysis' section.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, analyze the key trends in revenue, EBITDA, and net income over the last 3 years.
2. Summarize the cash flow from operations, investing, and financing activities.
3. Identify and explain the primary drivers for these trends as mentioned in the Management's Discussion and Analysis (MD&A).
4. Present the information clearly and concisely.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Historical Financial Analysis' Section:**''',
            'retrieval_prompt': 'Historical financial performance data, including revenue, EBITDA, net income, and cash flow trends from MD&A sections.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.2,
                'max_tokens': 2500
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'financial_analysis', 'mda']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 3. Liquidity Analysis
        {
            'name': 'RAG_Memo_Liquidity_Analysis_V2',
            'description': 'Generates liquidity analysis using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a credit analyst focused on liquidity risk. Your task is to write the 'Liquidity Analysis' section.

**Instructions:**
1. Using ONLY the retrieved document chunks below, assess the company's liquidity position.
2. Extract and discuss key metrics like cash and cash equivalents, working capital, and current ratio if available.
3. Summarize the company's primary sources of liquidity (e.g., cash from operations, revolving credit facilities).
4. Mention any discussion of liquidity challenges or strategies from the source text.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Liquidity Analysis' Section:**''',
            'retrieval_prompt': 'Information regarding liquidity, capital resources, cash position, working capital, current ratio, and revolving credit facilities from financial filings.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.1,
                'max_tokens': 2000
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'liquidity', 'balance_sheet']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 4. Leverage Analysis
        {
            'name': 'RAG_Memo_Leverage_Analysis_V2',
            'description': 'Generates leverage analysis using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a credit analyst evaluating a company's debt burden. Your task is to write the 'Leverage' section.

**Instructions:**
1. From the retrieved document chunks below, identify the company's total debt and describe its capital structure (e.g., breakdown of senior secured, unsecured notes, etc.).
2. If available, state the company's leverage ratio (e.g., Debt-to-EBITDA).
3. Summarize any commentary on the company's leverage policy or debt management strategy.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Leverage' Section:**''',
            'retrieval_prompt': 'Information about debt structure, leverage ratios, total debt, and capital structure from the MD&A section and debt footnote.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.1,
                'max_tokens': 2000
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'leverage', 'debt_structure']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 5. Refinancing Risks
        {
            'name': 'RAG_Memo_Refinancing_Risks_V2',
            'description': 'Generates refinancing risks analysis using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a credit analyst focused on refinancing risk. Your task is to write the 'Refinancing Risks' section.

**Instructions:**
1. Based on the retrieved document chunks below, identify debt maturities over the next 3-5 years.
2. Assess the magnitude of refinancing needs relative to the company's size.
3. Mention any commentary from management about refinancing plans or market access.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Refinancing Risks' Section:**''',
            'retrieval_prompt': 'Information about debt maturity schedule, upcoming refinancing needs, and management commentary on future financing plans.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.1,
                'max_tokens': 1800
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'refinancing_risk', 'debt_maturity']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 6. Debt Maturity Schedule
        {
            'name': 'RAG_Memo_Debt_Maturity_Schedule_V2',
            'description': 'Generates debt maturity schedule using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a financial analyst creating a debt maturity schedule. Your task is to write the 'Debt Maturity Schedule' section.

**Instructions:**
1. From the retrieved document chunks below, extract details about the maturity dates and amounts of the company's debt.
2. Present this information in a clear, tabular format if possible.
3. Include details like facility type, maturity date, amount outstanding, and interest rate where available.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Debt Maturity Schedule' Section:**''',
            'retrieval_prompt': 'Detailed debt maturity information, including facility types, amounts, maturity dates, and interest rates from the debt footnote and financing sections.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.1,
                'max_tokens': 2000
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'debt_schedule', 'maturity_profile']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 7. Facility Request
        {
            'name': 'RAG_Memo_Facility_Request_V2',
            'description': 'Generates facility request analysis using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a deal originator documenting a proposed transaction. Your task is to write the 'Facility Request' section.

**Instructions:**
1. Based on the retrieved document chunks below (term sheet, prospectus, etc.), detail the proposed facility amount, purpose, and use of proceeds.
2. Mention the term/maturity, pricing (if available), and any key covenants or terms.
3. Describe how the proposed facility fits into the borrower's overall capital structure.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Facility Request' Section:**''',
            'retrieval_prompt': 'Details of proposed transactions, including loan amount, purpose, use of proceeds, term, and pricing from prospectus or deal term sheets.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.1,
                'max_tokens': 2000
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'facility_request', 'term_sheet', 'prospectus']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 8. Obligor Assessment
        {
            'name': 'RAG_Memo_Obligor_Assessment_V2',
            'description': 'Generates obligor assessment using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a legal and financial analyst. Your task is to write the 'Obligor Assessment' section.

**Instructions:**
1. Based on the retrieved document chunks below, identify the specific legal entity (or entities) that will be the borrower/obligor for the proposed facility.
2. Describe the obligor's position within the parent company's corporate structure.
3. Mention any guarantees from the parent company or other subsidiaries, if described in the context.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Obligor Assessment' Section:**''',
            'retrieval_prompt': 'Information on corporate structure, including subsidiaries, parent company guarantees, and specific legal entities acting as obligors.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.2,
                'max_tokens': 1800
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'obligor', 'guarantor', 'legal']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 9. Key Risks
        {
            'name': 'RAG_Memo_Key_Risks_V2',
            'description': 'Generates key risks analysis using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a risk analyst. Your task is to write the 'Key Risks' section, summarizing the most critical risks.

**Instructions:**
1. Review the retrieved document chunks below, paying close attention to the 'Risk Factors' section.
2. Synthesize and summarize the 3-5 most material risks to the company's business and financial stability.
3. Categorize risks where possible (e.g., Operational, Market, Financial, Regulatory).
4. Be concise and focus on the risks most relevant to a lender.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Key Risks' Section:**''',
            'retrieval_prompt': 'The \'Risk Factors\' section and other risk disclosures from financial filings, detailing business and financial risks.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.3,
                'max_tokens': 2500
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'risk_factors', 'credit_risk']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        },
        # 10. Stock Price Analysis
        {
            'name': 'RAG_Memo_Stock_Price_Analysis_V2',
            'description': 'Generates stock price analysis using chunk-based RAG without variables',
            'tenant_type': TenantType.FINANCIAL_REPORT,
            'task_type': TaskType.RAG,
            'element_type': ElementType.PROMPT_TEMPLATE,
            'created_by': default_user_id,
            'generation_prompt': '''You are a market analyst. Your task is to provide a brief 'Stock Price Analysis' based on the company's own disclosures.

**Instructions:**
1. Based ONLY on the retrieved document chunks below, summarize the company's description of its stock performance.
2. Mention the exchange it trades on and its ticker symbol.
3. If the context includes a stock performance graph or comparison to an index (like the S&P 500), describe it.
4. Note any information on dividend policy or stock repurchase programs.

**Retrieved Document Chunks:**
{retrieved_chunks}

{additional_instructions}

**Generated 'Stock Price Analysis' Section:**''',
            'retrieval_prompt': 'Information regarding stock performance, stock ticker, trading market, and comparison to market indices from market equity sections.',
            'execution_config': {
                'model': 'gpt-4-turbo',
                'temperature': 0.2,
                'max_tokens': 2000
            },
            'tags': create_tags(['finance', 'rag', 'memo', 'stock_price', 'market_analysis']),
            'version': '2.0.0',
            'status': ElementStatus.ACTIVE,
            'is_system_default': True
        }
    ]
    
    # Insert templates
    inserted_count = 0
    skipped_count = 0
    failed_count = 0
    
    for template_data in templates_data:
        try:
            # Check for existing template
            existing = await ElementTemplate.find_one(
                ElementTemplate.name == template_data['name']
            )
            
            if existing:
                print(f'⚠️  Template {template_data["name"]} already exists, skipping...')
                skipped_count += 1
                continue
            
            # Create and insert template
            template = ElementTemplate(**template_data)
            await template.insert()
            
            print(f'✅ Inserted template: {template.name} (ID: {template.id})')
            inserted_count += 1
            
        except Exception as e:
            print(f'❌ Failed to insert template {template_data["name"]}: {e}')
            failed_count += 1
    
    # Print summary
    print("\n" + "="*60)
    print("FINANCIAL ELEMENT TEMPLATES V2 INSERTION SUMMARY (COMPLETE)")
    print("="*60)
    print(f"Total Templates: {len(templates_data)}")
    print(f"Successfully Inserted: {inserted_count}")
    print(f"Skipped (Already Exist): {skipped_count}")
    print(f"Failed: {failed_count}")
    print("="*60)
    
    client.close()
    return {
        "total": len(templates_data),
        "inserted": inserted_count,
        "skipped": skipped_count,
        "failed": failed_count
    }


async def main():
    """Main function."""
    try:
        result = await insert_financial_templates_v2()
        print(f"\n🎯 Operation completed successfully: {result}")
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 