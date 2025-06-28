# Tenant-Specific Element Insertion Scripts

This directory contains Python scripts for manually inserting predefined elements into the MongoDB database for different tenant types.

## Structure

- **`base_inserter.py`** - Base abstract class with common functionality
- **`config.py`** - Configuration and environment setup
- **`tenant_*_elements.py`** - Tenant-specific element definitions and insertion scripts
- **`insert_all.py`** - Script to run all tenant insertions at once

## Usage

### Prerequisites

1. Ensure TinyRAG services are running:
   ```bash
   cd ../.. && docker-compose up -d
   ```

2. Install dependencies (if running outside Docker):
   ```bash
   pip install -r requirements.txt
   ```

### Running Individual Tenant Scripts

```bash
# Insert HR elements
python tenant_hr_elements.py

# Insert Coding elements  
python tenant_coding_elements.py

# Insert Financial Report elements
python tenant_financial_elements.py

# Insert Deep Research elements
python tenant_research_elements.py

# Insert QA Generation elements
python tenant_qa_elements.py

# Insert Raw RAG elements
python tenant_raw_rag_elements.py
```

### Running All Tenant Scripts

```bash
python insert_all.py
```

## Configuration

Update `config.py` with your:
- MongoDB connection URL
- Database name
- Default user ID for ownership
- Default project IDs for each tenant

## Element Types Supported

- **PROMPT_TEMPLATE** - LLM prompt templates
- **MCP_CONFIG** - Model Context Protocol configurations
- **AGENTIC_TOOL** - Agentic workflow tools
- **RAG_CONFIG** - RAG-specific configurations

## Safety Features

- **Dry-run mode** - Test without actually inserting
- **Duplicate checking** - Prevents duplicate element names per project
- **Validation** - Validates element structure before insertion
- **Rollback support** - Track inserted elements for potential cleanup 