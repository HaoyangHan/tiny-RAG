"""
Financial Report Tenant Element Insertion Script.

This script contains predefined elements for Financial Report tenant type, including
agentic workflows for financial analysis and reporting automation.
"""

import asyncio
from typing import List, Dict, Any

from models.enums import TenantType, TaskType, ElementType, ElementStatus
from .base_inserter import BaseElementInserter


class FinancialElementInserter(BaseElementInserter):
    """Element inserter for Financial Report tenant type."""
    
    def get_elements_data(self) -> List[Dict[str, Any]]:
        """
        Get predefined Financial Report elements.
        
        Returns:
            List[Dict[str, Any]]: List of Financial Report element data
        """
        return [
            # Financial Statement Analyzer
            {
                "name": "Financial Statement Analyzer",
                "description": "Comprehensive template for analyzing financial statements and metrics",
                "task_type": TaskType.AGENTIC_WORKFLOW,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Analyze the following financial statement and provide comprehensive insights:

**Financial Statement Information:**
- Company: {company_name}
- Period: {reporting_period}
- Statement Type: {statement_type}
- Currency: {currency}

**Financial Data:**
{financial_data}

**Analysis Context:**
{analysis_context}

**Provide a detailed financial analysis covering:**

1. **Financial Performance Summary**
   - Key financial metrics and ratios
   - Revenue and profitability trends
   - Year-over-year growth analysis

2. **Liquidity Analysis**
   - Current ratio and quick ratio
   - Cash flow analysis
   - Working capital management

3. **Profitability Analysis**
   - Gross, operating, and net profit margins
   - Return on assets (ROA) and return on equity (ROE)
   - Earnings per share (EPS) trends

4. **Efficiency Metrics**
   - Asset turnover ratios
   - Inventory and receivables management
   - Operational efficiency indicators

5. **Financial Stability Assessment**
   - Debt-to-equity ratio
   - Interest coverage ratio
   - Financial leverage analysis

6. **Risk Assessment**
   - Credit risk indicators
   - Market risk exposure
   - Operational risk factors

7. **Strategic Insights**
   - Competitive position analysis
   - Investment opportunities
   - Recommendations for improvement

**Format the analysis with clear sections, supporting data, and actionable recommendations.**""",
                    variables=["company_name", "reporting_period", "statement_type", "currency", "financial_data", "analysis_context"],
                    execution_config={
                        "temperature": 0.2,
                        "max_tokens": 3000,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["financial_analysis", "metrics", "performance", "risk_assessment"])
            },
            
            # Budget Variance Report Generator
            {
                "name": "Budget Variance Report Generator",
                "description": "Template for generating budget variance analysis reports",
                "task_type": TaskType.AGENTIC_WORKFLOW,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Generate a comprehensive budget variance report:

**Budget Information:**
- Department/Unit: {department}
- Budget Period: {budget_period}
- Budget Category: {budget_category}
- Reporting Manager: {manager_name}

**Budget vs Actual Data:**
{budget_actual_data}

**External Factors:**
{external_factors}

**Generate a variance report that includes:**

1. **Executive Summary**
   - Overall budget performance
   - Key variance highlights
   - Critical action items

2. **Variance Analysis by Category**
   - Revenue variances
   - Expense variances by category
   - Capital expenditure variances

3. **Variance Calculations**
   - Absolute variances (Actual - Budget)
   - Percentage variances
   - Cumulative variances

4. **Root Cause Analysis**
   - Factors contributing to variances
   - Internal vs external drivers
   - Controllable vs uncontrollable factors

5. **Impact Assessment**
   - Financial impact of variances
   - Effect on overall department/company performance
   - Risk implications

6. **Corrective Actions**
   - Immediate corrective measures
   - Process improvements
   - Budget revision recommendations

7. **Forecast Adjustments**
   - Updated projections for remaining period
   - Risk-adjusted forecasts
   - Scenario planning considerations

**Present the report in a clear, executive-friendly format with charts and tables where appropriate.**""",
                    variables=["department", "budget_period", "budget_category", "manager_name", "budget_actual_data", "external_factors"],
                    execution_config={
                        "temperature": 0.3,
                        "max_tokens": 2800,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["budget", "variance", "analysis", "reporting"])
            },
            
            # Investment Portfolio Analyzer
            {
                "name": "Investment Portfolio Analyzer",
                "description": "Template for comprehensive investment portfolio analysis",
                "task_type": TaskType.AGENTIC_WORKFLOW,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Analyze the investment portfolio and provide comprehensive investment insights:

**Portfolio Information:**
- Portfolio Name: {portfolio_name}
- Investment Objective: {investment_objective}
- Risk Tolerance: {risk_tolerance}
- Time Horizon: {time_horizon}
- Total Portfolio Value: {portfolio_value}

**Holdings Data:**
{holdings_data}

**Market Context:**
{market_context}

**Provide comprehensive portfolio analysis:**

1. **Portfolio Overview**
   - Asset allocation breakdown
   - Geographic diversification
   - Sector distribution

2. **Performance Analysis**
   - Total return calculation
   - Risk-adjusted returns (Sharpe ratio)
   - Benchmark comparison

3. **Risk Assessment**
   - Portfolio volatility analysis
   - Value at Risk (VaR) calculation
   - Correlation analysis between holdings

4. **Diversification Analysis**
   - Diversification benefits
   - Concentration risk assessment
   - Asset class correlation

5. **Individual Holdings Review**
   - Top performers and underperformers
   - Position sizing analysis
   - Quality assessment of individual investments

6. **Rebalancing Recommendations**
   - Current vs target allocation
   - Rebalancing opportunities
   - Tax-efficient rebalancing strategies

7. **Strategic Recommendations**
   - Portfolio optimization suggestions
   - Risk management improvements
   - Investment opportunities and exits

**Include quantitative metrics, visual representations, and actionable investment recommendations.**""",
                    variables=["portfolio_name", "investment_objective", "risk_tolerance", "time_horizon", "portfolio_value", "holdings_data", "market_context"],
                    execution_config={
                        "temperature": 0.2,
                        "max_tokens": 2900,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["investment", "portfolio", "risk_analysis", "optimization"])
            },
            
            # Financial Compliance Checker
            {
                "name": "Financial Compliance Checker Agent",
                "description": "Agentic tool for automated financial compliance checking",
                "task_type": TaskType.AGENTIC_WORKFLOW,
                "element_type": ElementType.AGENTIC_TOOL,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Financial Compliance Checker Agent

An intelligent agent that automatically reviews financial documents and reports
for compliance with regulatory requirements and internal policies.

**Agent Capabilities:**
1. **Regulatory Compliance**
   - GAAP/IFRS compliance checking
   - SOX compliance verification
   - Industry-specific regulation adherence

2. **Policy Compliance**
   - Internal financial policies
   - Approval workflow compliance
   - Documentation requirements

3. **Data Validation**
   - Mathematical accuracy verification
   - Cross-reference validation
   - Consistency checking across documents

**Input Parameters:**
- Document Type: {document_type}
- Regulatory Framework: {regulatory_framework}
- Compliance Scope: {compliance_scope}
- Risk Level: {risk_level}

**Agent Workflow:**
1. Parse financial document structure
2. Identify applicable compliance requirements
3. Perform automated compliance checks
4. Flag potential violations or issues
5. Generate compliance report with recommendations

**Compliance Check Categories:**
```json
{
  "regulatory_checks": {
    "gaap_compliance": true,
    "disclosure_requirements": true,
    "calculation_accuracy": true
  },
  "policy_checks": {
    "approval_workflow": true,
    "documentation_completeness": true,
    "authorization_limits": true
  },
  "data_quality": {
    "mathematical_accuracy": true,
    "consistency_checks": true,
    "completeness_validation": true
  }
}
```

**Output Format:**
```json
{
  "compliance_status": "COMPLIANT|NON_COMPLIANT|REQUIRES_REVIEW",
  "violation_count": 0,
  "issues_found": [],
  "recommendations": [],
  "risk_score": 2.3,
  "approval_status": "APPROVED|PENDING|REJECTED"
}
```

**Configuration:**
- Compliance strictness: {strictness_level}
- Auto-approval threshold: {auto_approval_threshold}
- Review escalation rules: {escalation_rules}""",
                    variables=["document_type", "regulatory_framework", "compliance_scope", "risk_level", "strictness_level", "auto_approval_threshold", "escalation_rules"],
                    execution_config={
                        "agent_type": "compliance_checker",
                        "processing_timeout": 120,
                        "accuracy_threshold": 0.99,
                        "auto_approval_enabled": True
                    }
                ),
                "tags": self.create_element_tags(["agentic", "compliance", "automation", "risk_management"])
            },
            
            # Financial Workflow Configuration
            {
                "name": "Financial Reporting Workflow",
                "description": "Agentic workflow configuration for automated financial reporting",
                "task_type": TaskType.AGENTIC_WORKFLOW,
                "element_type": ElementType.AGENTIC_TOOL,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Financial Reporting Workflow Configuration

Automated workflow for end-to-end financial reporting process including
data collection, analysis, report generation, and approval routing.

**Workflow Stages:**
1. **Data Collection**
   - Source system integration
   - Data validation and cleansing
   - Consolidation processes

2. **Analysis and Calculation**
   - Financial metric computation
   - Variance analysis
   - Trend analysis

3. **Report Generation**
   - Template-based report creation
   - Chart and visualization generation
   - Executive summary creation

4. **Review and Approval**
   - Automated compliance checking
   - Stakeholder review routing
   - Approval workflow management

**Workflow Parameters:**
- Reporting Frequency: {reporting_frequency}
- Data Sources: {data_sources}
- Report Recipients: {report_recipients}
- Approval Chain: {approval_chain}

**Automation Rules:**
```json
{
  "triggers": {
    "schedule": "{reporting_frequency}",
    "data_availability": true,
    "manual_trigger": true
  },
  "validations": {
    "data_completeness": 95,
    "calculation_accuracy": 100,
    "compliance_score": 90
  },
  "notifications": {
    "completion": true,
    "errors": true,
    "approvals_pending": true
  }
}
```

**Integration Points:**
- ERP Systems: {erp_integration}
- BI Tools: {bi_integration}
- Document Management: {document_system}
- Approval Systems: {approval_system}

**Quality Controls:**
- Automated reconciliation: {auto_reconciliation}
- Exception handling: {exception_handling}
- Audit trail: {audit_trail}""",
                    variables=["reporting_frequency", "data_sources", "report_recipients", "approval_chain", "erp_integration", "bi_integration", "document_system", "approval_system", "auto_reconciliation", "exception_handling", "audit_trail"],
                    execution_config={
                        "workflow_engine": "financial_reporting",
                        "max_execution_time": 3600,
                        "retry_attempts": 3,
                        "error_escalation": True
                    }
                ),
                "tags": self.create_element_tags(["workflow", "automation", "reporting", "integration"])
            }
        ]


async def main():
    """Main function to run Financial Report element insertion."""
    inserter = FinancialElementInserter(TenantType.FINANCIAL_REPORT)
    result = await inserter.run()
    
    print("\n" + "="*60)
    print("FINANCIAL REPORT ELEMENT INSERTION SUMMARY")
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