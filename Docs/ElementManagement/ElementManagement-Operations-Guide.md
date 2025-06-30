# Element Management Operations Guide

## Quick Start

### Prerequisites
1. **TinyRAG Services Running**:
   ```bash
   cd /path/to/tiny-RAG
   docker-compose up -d
   ```

2. **Environment Setup**:
   ```bash
   export MONGODB_URL="mongodb://localhost:27017"
   export SUMMARIZATION_LLM_PROVIDER="openai"
   export SUMMARIZATION_LLM_MODEL="gpt-4o-mini"
   export OPENAI_API_KEY="your-api-key"
   ```

3. **Navigate to Scripts**:
   ```bash
   cd rag-memo-api/scripts/element_management
   ```

## Core Operations

### 1. Template Management

#### Insert Element Templates
```bash
# Insert all tenant templates (recommended first run)
python insert_element_templates.py

# Insert specific tenant templates
python insert_element_templates.py --tenant hr
python insert_element_templates.py --tenant coding
python insert_element_templates.py --tenant financial_report

# Dry run to test (no actual insertion)
python insert_element_templates.py --dry-run

# Force update existing templates
python insert_element_templates.py --force-update

# Insert with custom configuration
python insert_element_templates.py --config custom_config.yaml
```

#### Manage Existing Templates
```bash
# List all templates
python manage_templates.py list

# List templates by tenant
python manage_templates.py list --tenant hr

# Show template details
python manage_templates.py show --template-id 507f1f77bcf86cd799439011

# Update template field
python manage_templates.py update --template-id 507f1f77bcf86cd799439011 --field description --value "Updated description"

# Update template version
python manage_templates.py version --template-id 507f1f77bcf86cd799439011 --version 1.1.0

# Activate/deactivate template
python manage_templates.py activate --template-id 507f1f77bcf86cd799439011
python manage_templates.py deactivate --template-id 507f1f77bcf86cd799439011

# Remove template (soft delete)
python manage_templates.py remove --template-id 507f1f77bcf86cd799439011

# Hard delete template (permanent)
python manage_templates.py delete --template-id 507f1f77bcf86cd799439011 --confirm
```

### 2. Project Element Provisioning

#### Automatic Provisioning (happens on project creation)
The system automatically provisions elements when:
- New project is created via API
- Project tenant type is identified
- Active templates exist for that tenant

#### Manual Provisioning
```bash
# Provision all templates to existing project
python provision_project.py --project-id 507f1f77bcf86cd799439012

# Provision specific templates only
python provision_project.py --project-id 507f1f77bcf86cd799439012 --template-ids 507f1f77bcf86cd799439011,507f1f77bcf86cd799439013

# Provision templates for specific tenant (useful for multi-tenant projects)
python provision_project.py --project-id 507f1f77bcf86cd799439012 --tenant hr

# Dry run provisioning
python provision_project.py --project-id 507f1f77bcf86cd799439012 --dry-run

# Force re-provision (replace existing default elements)
python provision_project.py --project-id 507f1f77bcf86cd799439012 --force

# Provision with custom element naming
python provision_project.py --project-id 507f1f77bcf86cd799439012 --prefix "Custom_"
```

### 3. Prompt Summarization

#### Generate Retrieval Prompts
```bash
# Generate retrieval prompts for all elements missing them
python generate_retrieval_prompts.py

# Generate for specific elements
python generate_retrieval_prompts.py --element-ids 507f1f77bcf86cd799439014,507f1f77bcf86cd799439015

# Generate for all elements in a project
python generate_retrieval_prompts.py --project-id 507f1f77bcf86cd799439012

# Generate for specific tenant type
python generate_retrieval_prompts.py --tenant hr

# Regenerate all (overwrite existing)
python generate_retrieval_prompts.py --regenerate-all

# Custom summarization settings
python generate_retrieval_prompts.py --max-tokens 200 --temperature 0.2

# Batch process with progress tracking
python generate_retrieval_prompts.py --batch-size 10 --show-progress
```

#### Test Prompt Quality
```bash
# Test prompt summarization quality
python test_prompt_summarization.py --sample-size 5

# Compare generation vs retrieval prompts
python test_prompt_summarization.py --compare --element-id 507f1f77bcf86cd799439014

# Validate summarization effectiveness
python test_prompt_summarization.py --validate-all
```

### 4. Cleanup and Removal

#### Remove Script-Inserted Elements
```bash
# Remove all elements inserted by scripts
python remove_script_elements.py

# Remove by tenant type
python remove_script_elements.py --tenant hr

# Remove by specific insertion batch
python remove_script_elements.py --batch-id batch_20241201_143022

# Remove elements from specific project
python remove_script_elements.py --project-id 507f1f77bcf86cd799439012

# Dry run removal (see what would be removed)
python remove_script_elements.py --dry-run

# Remove only default elements (preserve user-created)
python remove_script_elements.py --default-only

# Force removal (bypass confirmations)
python remove_script_elements.py --force
```

#### Template Cleanup
```bash
# Remove unused templates (not referenced by any elements)
python cleanup_templates.py --unused

# Remove outdated template versions
python cleanup_templates.py --outdated --keep-latest 2

# Archive old templates (soft delete with archive flag)
python cleanup_templates.py --archive --older-than 90d

# Clean up test/development templates
python cleanup_templates.py --test-data

# Remove templates by status
python cleanup_templates.py --status DEPRECATED
```

### 5. Monitoring and Analytics

#### System Status
```bash
# Check system health
python system_status.py

# Template usage statistics
python system_status.py --templates

# Element distribution by tenant
python system_status.py --distribution

# Prompt summarization metrics
python system_status.py --summarization

# Performance metrics
python system_status.py --performance
```

#### Generate Reports
```bash
# Generate usage report
python generate_reports.py --type usage --output usage_report.html

# Template effectiveness report
python generate_reports.py --type effectiveness --tenant hr

# System health report
python generate_reports.py --type health --format json

# Custom date range report
python generate_reports.py --type usage --from 2024-01-01 --to 2024-12-31
```

## Configuration Files

### Main Configuration (`config/element_management.yaml`)
```yaml
# Database Settings
mongodb:
  url: "mongodb://localhost:27017"
  database: "tinyrag"
  
# LLM Configuration for Summarization
summarization:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.3
  max_tokens: 500
  timeout: 30
  
# Element Management
element_management:
  auto_provision_templates: true
  enable_retrieval_prompt_generation: true
  default_template_version: "1.0.0"
  batch_size: 10
  
# Cleanup Settings
cleanup:
  archive_older_than_days: 90
  keep_latest_versions: 3
  remove_unused_after_days: 30
```

### Tenant Configuration (`config/tenant_settings.yaml`)
```yaml
tenants:
  hr:
    display_name: "Human Resources"
    auto_provision: true
    default_llm_config:
      temperature: 0.3
      max_tokens: 2000
    allowed_element_types:
      - PROMPT_TEMPLATE
      - RAG_CONFIG
      
  coding:
    display_name: "Software Development"
    auto_provision: true
    default_llm_config:
      temperature: 0.2
      max_tokens: 2500
    allowed_element_types:
      - PROMPT_TEMPLATE
      - MCP_CONFIG
      - AGENTIC_TOOL
```

### Summarization Prompts (`config/summarization_prompts.yaml`)
```yaml
# Main summarization prompt
main_prompt: |
  Create a concise, searchable summary of the following detailed prompt.
  Focus on key concepts, main objectives, and searchable terms.
  Keep it under {max_tokens} tokens while preserving essential meaning.
  
  Original prompt:
  {generation_prompt}
  
  Summary:

# Tenant-specific prompts
tenant_prompts:
  hr: |
    Summarize this HR-related prompt focusing on policy areas, employee processes, and compliance topics.
  coding: |
    Summarize this development prompt focusing on programming concepts, tools, and technical processes.
  financial_report: |
    Summarize this financial prompt focusing on analysis types, metrics, and reporting objectives.
```

## Troubleshooting

### Common Issues

#### Templates Not Appearing in Projects
```bash
# Check if templates exist for tenant
python manage_templates.py list --tenant hr

# Check project tenant type
python check_project.py --project-id 507f1f77bcf86cd799439012

# Force provision templates
python provision_project.py --project-id 507f1f77bcf86cd799439012 --force
```

#### Retrieval Prompt Generation Failing
```bash
# Check LLM configuration
python test_llm_connection.py

# Test with specific element
python generate_retrieval_prompts.py --element-ids 507f1f77bcf86cd799439014 --debug

# Check element prompt length
python check_prompt_length.py --element-id 507f1f77bcf86cd799439014
```

#### Element Removal Not Working
```bash
# Check element metadata
python check_element.py --element-id 507f1f77bcf86cd799439014

# List elements by insertion source
python list_elements.py --created-by script

# Force removal with debug
python remove_script_elements.py --element-id 507f1f77bcf86cd799439014 --force --debug
```

### Debug Mode
Enable debug mode for detailed logging:
```bash
export ELEMENT_MANAGEMENT_DEBUG=true
export LOG_LEVEL=DEBUG
```

### Performance Optimization
```bash
# Enable batch processing
export BATCH_PROCESSING=true
export BATCH_SIZE=20

# Use connection pooling
export MONGODB_POOL_SIZE=20
export MONGODB_POOL_TIMEOUT=30
```

## Best Practices

### Template Management
1. **Test First**: Always use `--dry-run` before making changes
2. **Version Control**: Increment versions when making significant changes
3. **Backup**: Export templates before major updates
4. **Monitor Usage**: Regularly check template usage statistics

### Element Operations
1. **Batch Operations**: Use batch processing for large operations
2. **Progress Tracking**: Monitor long-running operations
3. **Error Handling**: Check logs for operation failures
4. **Cleanup**: Regularly clean up unused or outdated elements

### Prompt Engineering
1. **Generation Prompts**: Include all necessary context and instructions
2. **Retrieval Prompts**: Focus on searchable keywords and concepts
3. **Testing**: Validate prompt effectiveness with sample data
4. **Optimization**: Continuously improve based on usage metrics

### System Maintenance
1. **Regular Monitoring**: Check system status weekly
2. **Performance Metrics**: Track response times and success rates
3. **Capacity Planning**: Monitor storage and processing requirements
4. **Updates**: Keep scripts and configurations up to date 